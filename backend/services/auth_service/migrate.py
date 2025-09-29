#!/usr/bin/env python3
"""
Database migration management script for auth service.

This script provides utilities to run database migrations using Alembic.
Requirements: 1.1, 1.2, 1.5, 1.6 - Database schema management
"""

import os
import sys
from alembic.config import Config
from alembic import command
from pathlib import Path


def get_alembic_config():
    """Get Alembic configuration."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    alembic_cfg_path = script_dir / "migrations" / "alembic.ini"
    
    if not alembic_cfg_path.exists():
        raise FileNotFoundError(f"Alembic config not found at {alembic_cfg_path}")
    
    alembic_cfg = Config(str(alembic_cfg_path))
    
    # Set the script location to the migrations directory
    alembic_cfg.set_main_option("script_location", str(script_dir / "migrations"))
    
    return alembic_cfg


def upgrade_database(revision="head"):
    """
    Upgrade database to the specified revision.
    
    Args:
        revision (str): Target revision (default: "head" for latest)
    """
    try:
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, revision)
        print(f"✅ Database upgraded to revision: {revision}")
    except Exception as e:
        print(f"❌ Error upgrading database: {e}")
        sys.exit(1)


def downgrade_database(revision):
    """
    Downgrade database to the specified revision.
    
    Args:
        revision (str): Target revision
    """
    try:
        alembic_cfg = get_alembic_config()
        command.downgrade(alembic_cfg, revision)
        print(f"✅ Database downgraded to revision: {revision}")
    except Exception as e:
        print(f"❌ Error downgrading database: {e}")
        sys.exit(1)


def show_current_revision():
    """Show current database revision."""
    try:
        alembic_cfg = get_alembic_config()
        command.current(alembic_cfg)
    except Exception as e:
        print(f"❌ Error getting current revision: {e}")
        sys.exit(1)


def show_migration_history():
    """Show migration history."""
    try:
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg)
    except Exception as e:
        print(f"❌ Error getting migration history: {e}")
        sys.exit(1)


def create_migration(message):
    """
    Create a new migration.
    
    Args:
        message (str): Migration message
    """
    try:
        alembic_cfg = get_alembic_config()
        command.revision(alembic_cfg, message=message, autogenerate=True)
        print(f"✅ Created new migration: {message}")
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        sys.exit(1)


def main():
    """Main CLI interface for migration management."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate.py upgrade [revision]  - Upgrade to revision (default: head)")
        print("  python migrate.py downgrade <revision> - Downgrade to revision")
        print("  python migrate.py current             - Show current revision")
        print("  python migrate.py history             - Show migration history")
        print("  python migrate.py create <message>    - Create new migration")
        sys.exit(1)
    
    command_name = sys.argv[1]
    
    if command_name == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade_database(revision)
    elif command_name == "downgrade":
        if len(sys.argv) < 3:
            print("❌ Downgrade requires a target revision")
            sys.exit(1)
        downgrade_database(sys.argv[2])
    elif command_name == "current":
        show_current_revision()
    elif command_name == "history":
        show_migration_history()
    elif command_name == "create":
        if len(sys.argv) < 3:
            print("❌ Create requires a migration message")
            sys.exit(1)
        create_migration(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command_name}")
        sys.exit(1)


if __name__ == "__main__":
    main()