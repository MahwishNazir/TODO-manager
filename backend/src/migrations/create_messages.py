"""
Migration: Create messages table for Phase III.

This migration creates the messages table to store conversation history
with proper indexes for chronological retrieval and task linking.

Prerequisites: conversations table exists, tasks table exists.
"""

UPGRADE_SQL = """
-- Create messages table (FR-011)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_mentioned_task_id INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Foreign key to conversations (FR-012)
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,

    -- Foreign key to tasks for context (FR-014, FR-019)
    CONSTRAINT fk_messages_task
        FOREIGN KEY (last_mentioned_task_id) REFERENCES tasks(id) ON DELETE SET NULL,

    -- Check constraint for role enum (FR-013)
    CONSTRAINT chk_messages_role
        CHECK (role IN ('user', 'assistant', 'system'))
);

-- Create indexes (FR-027)
CREATE INDEX IF NOT EXISTS idx_messages_conversation
    ON messages (conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_time
    ON messages (conversation_id, created_at);
"""

DOWNGRADE_SQL = """
-- Drop indexes
DROP INDEX IF EXISTS idx_messages_conversation_time;
DROP INDEX IF EXISTS idx_messages_conversation;

-- Drop table
DROP TABLE IF EXISTS messages;
"""


async def upgrade(connection) -> None:
    """Apply the migration."""
    await connection.execute(UPGRADE_SQL)


async def downgrade(connection) -> None:
    """Revert the migration."""
    await connection.execute(DOWNGRADE_SQL)
