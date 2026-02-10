"""
Database migration runner for Phase III.

This module provides utilities to run database migrations in order.
Migrations are executed sequentially to ensure proper dependency handling.

Usage:
    from src.migrations import run_all_migrations
    await run_all_migrations(database_url)
"""

from typing import Optional
import asyncio
import importlib
import logging

# Migration order - execute in this sequence
MIGRATION_ORDER = [
    "add_task_extensions",
    "create_conversations",
    "create_messages",
]

logger = logging.getLogger(__name__)


async def run_migration(connection, migration_name: str, direction: str = "upgrade") -> None:
    """Run a single migration.

    Args:
        connection: Database connection
        migration_name: Name of the migration module
        direction: 'upgrade' or 'downgrade'
    """
    module = importlib.import_module(f"src.migrations.{migration_name}")
    func = getattr(module, direction)
    await func(connection)
    logger.info(f"Migration {migration_name} {direction} completed")


async def run_all_migrations(connection, direction: str = "upgrade") -> None:
    """Run all migrations in order.

    Args:
        connection: Database connection
        direction: 'upgrade' to apply, 'downgrade' to revert
    """
    migrations = MIGRATION_ORDER if direction == "upgrade" else reversed(MIGRATION_ORDER)
    for migration_name in migrations:
        await run_migration(connection, migration_name, direction)


def get_migration_sql(migration_name: str, direction: str = "upgrade") -> str:
    """Get the raw SQL for a migration.

    Args:
        migration_name: Name of the migration module
        direction: 'upgrade' or 'downgrade'

    Returns:
        SQL string for the migration
    """
    module = importlib.import_module(f"src.migrations.{migration_name}")
    sql_attr = f"{direction.upper()}_SQL"
    return getattr(module, sql_attr, "")
