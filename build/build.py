"""Build script for Wareflow Employee Management System.

This script provides automated build functionality for creating standalone
executables using PyInstaller. It can be run locally or used in CI/CD.

Usage:
    python build/build.py
    python build/build.py --clean
    python build/build.py --version 1.2.3
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_version():
    """Get version from git tags or __init__.py."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    # Fallback to reading from __init__.py
    init_file = Path("src/employee_manager.py")
    if init_file.exists():
        content = init_file.read_text()
        for line in content.split("\n"):
            if "__version__" in line:
                return line.split("=")[1].strip().strip('"').strip("'")

    return "unknown"


def run_command(cmd, cwd=None):
    """Run a command and display output."""
    print(f"\n> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_name}")

    # Clean spec files from build directory
    for spec_file in Path(".").glob("*.spec"):
        if spec_file.name != "wems.spec":
            spec_file.unlink()
            print(f"  Removed: {spec_file}")


def run_tests():
    """Run tests before building."""
    print("\nRunning tests...")
    run_command(["uv", "run", "pytest", "--cov=src", "--ignore=tests/test_ui"])


def build_executable(version, clean=False):
    """Build the executable using PyInstaller."""
    print(f"\nBuilding wems version {version}...")

    if clean:
        clean_build()

    # Run tests first
    run_tests()

    # Build with PyInstaller
    spec_file = Path("build/wems.spec")
    if not spec_file.exists():
        print(f"Error: Spec file not found: {spec_file}")
        sys.exit(1)

    run_command(["uv", "run", "pyinstaller", str(spec_file), "--clean", "--noconfirm"])

    # Generate checksums
    print("\nGenerating checksums...")
    dist_dir = Path("dist")
    artifacts = []

    if os.name == "nt":  # Windows
        exe_files = list(dist_dir.glob("wems/*.exe"))
    else:
        exe_files = list(dist_dir.glob("wems/wems")) + list(dist_dir.glob("wems/wems.bin"))

    for exe_file in exe_files:
        sha256_hash = hashlib.sha256()
        with open(exe_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        checksum = sha256_hash.hexdigest()
        checksum_file = dist_dir / f"{exe_file.name}.sha256"

        with open(checksum_file, "w") as f:
            f.write(f"{checksum}  {exe_file.name}\n")

        print(f"  {exe_file.name}: {checksum}")
        artifacts.append((exe_file, checksum))

    print("\n✅ Build complete!")
    print(f"\nArtifacts created:")
    for artifact, checksum in artifacts:
        print(f"  - {artifact}")
        print(f"    SHA256: {checksum}")

    return artifacts


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Wareflow Employee Management System"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Override version (default: from git tags)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests before building"
    )

    args = parser.parse_args()

    # Get version
    if args.version:
        version = args.version
    else:
        version = get_version()

    # Skip tests if requested
    if args.skip_tests:
        global run_tests
        run_tests = lambda: None

    # Build
    build_executable(version, clean=args.clean)


if __name__ == "__main__":
    main()
