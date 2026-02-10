"""
Migration: Add Task model extensions for Phase III.

This migration adds priority, status, due_date, and is_deleted fields
to the existing tasks table, along with partial indexes for optimized queries.

Prerequisites: Phase II tasks table exists with id, user_id, title,
               is_completed, created_at, updated_at columns.
"""

# SQL statements for migration
UPGRADE_SQL = """
-- Add new columns to tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) NOT NULL DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'incomplete';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date DATE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;

-- Add CHECK constraints for enum values
ALTER TABLE tasks ADD CONSTRAINT chk_tasks_priority
    CHECK (priority IN ('low', 'medium', 'high'));
ALTER TABLE tasks ADD CONSTRAINT chk_tasks_status
    CHECK (status IN ('incomplete', 'complete'));

-- Migrate existing is_completed values to status
UPDATE tasks SET status = CASE
    WHEN is_completed = TRUE THEN 'complete'
    ELSE 'incomplete'
END;

-- Create indexes for efficient queries (FR-025)
CREATE INDEX IF NOT EXISTS idx_tasks_user_status
    ON tasks (user_id, status) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date
    ON tasks (user_id, due_date) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_tasks_user_deleted
    ON tasks (user_id, is_deleted);
"""

DOWNGRADE_SQL = """
-- Remove indexes
DROP INDEX IF EXISTS idx_tasks_user_deleted;
DROP INDEX IF EXISTS idx_tasks_user_due_date;
DROP INDEX IF EXISTS idx_tasks_user_status;

-- Remove constraints
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_tasks_status;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_tasks_priority;

-- Remove columns
ALTER TABLE tasks DROP COLUMN IF EXISTS is_deleted;
ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;
ALTER TABLE tasks DROP COLUMN IF EXISTS status;
ALTER TABLE tasks DROP COLUMN IF EXISTS priority;
"""


async def upgrade(connection) -> None:
    """Apply the migration."""
    await connection.execute(UPGRADE_SQL)


async def downgrade(connection) -> None:
    """Revert the migration."""
    await connection.execute(DOWNGRADE_SQL)
