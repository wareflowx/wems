"""Application lock management commands."""

import os
import socket

import typer

from lock.manager import LockManager
from lock.models import AppLock

app = typer.Typer(help="Gestion du verrou applicatif")


def get_process_info():
    """Get current process identification."""
    hostname = socket.gethostname()
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    pid = os.getpid()
    return hostname, username, pid


@app.command()
def status():
    """Afficher le statut du verrou applicatif."""
    hostname, username, pid = get_process_info()

    active_lock = AppLock.get_active_lock()

    if not active_lock:
        typer.echo("🔓 État du verrou applicatif")
        typer.echo("")
        typer.echo("  Statut:    🔓 Libre")
        typer.echo("  Aucun verrou actif")
        raise typer.Exit(0)

    # Check if we own the lock
    we_own_it = active_lock.hostname == hostname and active_lock.process_id == pid

    typer.echo("🔒 État du verrou applicatif")
    typer.echo("")
    typer.echo("  Statut:    🔒 Verrouillé")
    typer.echo("")
    typer.echo("  Propriétaire:")
    typer.echo(f"    Hostname: {active_lock.hostname}")
    typer.echo(f"    User:     {active_lock.username or 'N/A'}")
    typer.echo(f"    PID:      {active_lock.process_id}")
    typer.echo("")
    typer.echo("  Temps:")
    typer.echo(f"    Acquis:       {active_lock.locked_at.strftime('%Y-%m-%d %H:%M:%S')}")
    typer.echo(f"    Heartbeat:    {active_lock.last_heartbeat.strftime('%Y-%m-%d %H:%M:%S')}")

    # Calculate age
    from datetime import datetime

    heartbeat_age = (datetime.now() - active_lock.last_heartbeat).total_seconds()
    lock_age = (datetime.now() - active_lock.locked_at).total_seconds()

    typer.echo(f"    Âge heartbeat: {int(heartbeat_age)} secondes")
    typer.echo(f"    Âge verrou:    {int(lock_age // 60)} minutes {int(lock_age % 60)} secondes")
    typer.echo("")

    if we_own_it:
        typer.echo("  ✅ Vous possédez ce verrou")
    else:
        typer.echo("  ⚠️  Vous ne possédez pas ce verrou")

    if active_lock.is_stale:
        typer.echo("  🔴 Ce verrou est périmé (stale)")


@app.command()
def acquire():
    """Acquérir le verrou applicatif."""
    hostname, username, pid = get_process_info()

    # Check if already locked
    active_lock = AppLock.get_active_lock()
    if active_lock:
        if active_lock.hostname == hostname and active_lock.process_id == pid:
            typer.echo("ℹ️  Vous possédez déjà le verrou")
            raise typer.Exit(0)

        if not active_lock.is_stale:
            typer.echo(f"❌ Verrou déjà acquis par {active_lock.hostname}")
            typer.echo(f"   Processus: {active_lock.process_id}")
            typer.echo(f"   Acquis: {active_lock.locked_at}")
            raise typer.Exit(1)

        # Lock is stale, will be cleaned up automatically
        typer.echo("⚠️  Ancien verrou périmé, nettoyage en cours...")

    # Create lock manager and acquire
    try:
        manager = LockManager(hostname=hostname, username=username, pid=pid)
        lock = manager.acquire_lock()

        typer.echo("✅ Verrou acquis avec succès")
        typer.echo("")
        typer.echo(f"  Hostname: {lock.hostname}")
        typer.echo(f"  User:     {lock.username or 'N/A'}")
        typer.echo(f"  PID:      {lock.process_id}")
        typer.echo(f"  Acquis:   {lock.locked_at.strftime('%Y-%m-%d %H:%M:%S')}")
        typer.echo("")
        typer.echo("💡 Le heartbeat sera rafraîchi automatiquement toutes les 30 secondes")
        typer.echo("💡 Utilisez 'python -m cli lock release' pour libérer le verrou")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de l'acquisition: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def release():
    """Libérer le verrou applicatif."""
    hostname, username, pid = get_process_info()

    # Check if we own the lock
    active_lock = AppLock.get_active_lock()
    if not active_lock:
        typer.echo("ℹ️  Aucun verrou actif")
        raise typer.Exit(0)

    we_own_it = active_lock.hostname == hostname and active_lock.process_id == pid

    if not we_own_it:
        typer.echo("❌ Vous ne possédez pas ce verrou")
        typer.echo(f"   Verrou détenu par: {active_lock.hostname}")
        typer.echo(f"   PID: {active_lock.process_id}")
        raise typer.Exit(1)

    # Release lock
    try:
        manager = LockManager(hostname=hostname, username=username, pid=pid)
        success = manager.release_lock()

        if success:
            typer.echo("✅ Verrou libéré avec succès")
        else:
            typer.echo("⚠️  Verrou non trouvé (peut-être déjà libéré)")

    except Exception as e:
        typer.echo(f"❌ Erreur lors de la libération: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def refresh():
    """Rafraîchir le heartbeat manuellement."""
    hostname, username, pid = get_process_info()

    # Check if we own the lock
    active_lock = AppLock.get_active_lock()
    if not active_lock:
        typer.echo("❌ Aucun verrou actif")
        raise typer.Exit(1)

    we_own_it = active_lock.hostname == hostname and active_lock.process_id == pid

    if not we_own_it:
        typer.echo("❌ Vous ne possédez pas ce verrou")
        raise typer.Exit(1)

    # Refresh heartbeat
    try:
        success = AppLock.refresh_heartbeat(hostname, pid)

        if success:
            from datetime import datetime

            typer.echo(f"✅ Heartbeat rafraîchi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            typer.echo("❌ Échec du rafraîchissement")
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Erreur lors du rafraîchissement: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def info():
    """Afficher les informations détaillées du verrou."""
    hostname, username, pid = get_process_info()

    active_lock = AppLock.get_active_lock()

    if not active_lock:
        typer.echo("Aucun verrou actif")
        raise typer.Exit(0)

    typer.echo("📋 Informations détaillées du verrou")
    typer.echo("")
    typer.echo(f"  ID:              {active_lock.id}")
    typer.echo(f"  Hostname:        {active_lock.hostname}")
    typer.echo(f"  Username:        {active_lock.username or 'N/A'}")
    typer.echo(f"  Process ID:      {active_lock.process_id}")
    typer.echo("")
    typer.echo(f"  Verrouillé à:    {active_lock.locked_at.strftime('%Y-%m-%d %H:%M:%S')}")
    typer.echo(f"  Dernier heartbeat: {active_lock.last_heartbeat.strftime('%Y-%m-%d %H:%M:%S')}")
    typer.echo("")

    # Check if stale
    if active_lock.is_stale:
        typer.echo("  🔴 Statut: PÉRIMÉ (STALE)")
        from datetime import datetime

        age = (datetime.now() - active_lock.last_heartbeat).total_seconds()
        typer.echo(f"     Dernier heartbeat il y a {int(age)} secondes")
    else:
        typer.echo("  🟢 Statut: ACTIF")

    # Check ownership
    if active_lock.hostname == hostname and active_lock.process_id == pid:
        typer.echo("  ✅ Propriétaire: Vous")
    else:
        typer.echo("  ⚠️  Propriétaire: Autre processus")
