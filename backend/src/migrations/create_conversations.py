"""
Migration: Create conversations table for Phase III.

This migration creates the conversations table to store AI chat sessions
with proper indexes for efficient user-based queries.

Prerequisites: Users table exists (Phase II).
"""

UPGRADE_SQL = """
-- Create conversations table (FR-007)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Add foreign key constraint to users table (FR-008)
-- Note: Commented out as users table may not have proper FK setup in Phase II
-- ALTER TABLE conversations ADD CONSTRAINT fk_conversations_user
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Create indexes (FR-026)
CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations (user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_active
    ON conversations (user_id, is_active) WHERE is_active = TRUE;
"""

DOWNGRADE_SQL = """
-- Drop indexes
DROP INDEX IF EXISTS idx_conversations_user_active;
DROP INDEX IF EXISTS idx_conversations_user_id;

-- Drop table
DROP TABLE IF EXISTS conversations;
"""


async def upgrade(connection) -> None:
    """Apply the migration."""
    await connection.execute(UPGRADE_SQL)


async def downgrade(connection) -> None:
    """Revert the migration."""
    await connection.execute(DOWNGRADE_SQL)
