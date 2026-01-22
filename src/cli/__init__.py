"""CLI commands for Simple Employee Manager."""

# This package contains CLI command modules but doesn't export app
# to avoid circular import with cli_main
# Import app directly from cli_main instead

from . import caces, employee, lock, medical, report, training

__all__ = ["employee", "caces", "medical", "training", "report", "lock"]
