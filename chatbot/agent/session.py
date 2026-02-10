"""
Session management module.

Provides session store interface with in-memory implementation.
Handles session creation, retrieval, update, and expiration.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4

from chatbot.agent.config import get_settings
from chatbot.agent.models import (
    AgentSession,
    ConfirmationState,
    ConversationContext,
    SessionStatus,
)


class SessionStore(ABC):
    """Abstract base class for session storage."""

    @abstractmethod
    async def create(self, user_id: str) -> AgentSession:
        """Create a new session for a user."""
        pass

    @abstractmethod
    async def get(self, session_id: UUID) -> Optional[AgentSession]:
        """Get a session by ID."""
        pass

    @abstractmethod
    async def update(self, session: AgentSession) -> AgentSession:
        """Update an existing session."""
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete a session."""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: str) -> list[AgentSession]:
        """Get all sessions for a user."""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        pass


class InMemorySessionStore(SessionStore):
    """
    In-memory session store for development.

    Sessions are stored in a dictionary and lost on restart.
    Suitable for development and testing only.
    """

    def __init__(self):
        self._sessions: Dict[UUID, AgentSession] = {}
        self._contexts: Dict[UUID, ConversationContext] = {}
        self._confirmations: Dict[UUID, ConfirmationState] = {}
        self._lock = asyncio.Lock()
        self._settings = get_settings()

    async def create(self, user_id: str) -> AgentSession:
        """Create a new session for a user."""
        async with self._lock:
            session = AgentSession(
                session_id=uuid4(),
                user_id=user_id,
            )
            self._sessions[session.session_id] = session
            self._contexts[session.session_id] = ConversationContext()
            self._confirmations[session.session_id] = ConfirmationState()
            return session

    async def get(self, session_id: UUID) -> Optional[AgentSession]:
        """Get a session by ID, checking expiration."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None

            # Check if expired
            if session.is_expired(self._settings.session_ttl_seconds):
                session.expire()
                return None

            return session

    async def update(self, session: AgentSession) -> AgentSession:
        """Update an existing session."""
        async with self._lock:
            if session.session_id not in self._sessions:
                raise ValueError(f"Session {session.session_id} not found")

            session.touch()
            self._sessions[session.session_id] = session
            return session

    async def delete(self, session_id: UUID) -> bool:
        """Delete a session and its associated data."""
        async with self._lock:
            if session_id not in self._sessions:
                return False

            del self._sessions[session_id]
            self._contexts.pop(session_id, None)
            self._confirmations.pop(session_id, None)
            return True

    async def get_by_user(self, user_id: str) -> list[AgentSession]:
        """Get all active sessions for a user."""
        async with self._lock:
            ttl = self._settings.session_ttl_seconds
            return [
                s for s in self._sessions.values()
                if s.user_id == user_id and not s.is_expired(ttl)
            ]

    async def cleanup_expired(self) -> int:
        """Remove expired sessions."""
        async with self._lock:
            ttl = self._settings.session_ttl_seconds
            expired = [
                sid for sid, session in self._sessions.items()
                if session.is_expired(ttl)
            ]

            for sid in expired:
                del self._sessions[sid]
                self._contexts.pop(sid, None)
                self._confirmations.pop(sid, None)

            return len(expired)

    # Context management

    async def get_context(self, session_id: UUID) -> Optional[ConversationContext]:
        """Get conversation context for a session."""
        async with self._lock:
            return self._contexts.get(session_id)

    async def set_context(
        self,
        session_id: UUID,
        context: ConversationContext
    ) -> None:
        """Set conversation context for a session."""
        async with self._lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session {session_id} not found")
            self._contexts[session_id] = context

    # Confirmation state management

    async def get_confirmation_state(
        self,
        session_id: UUID
    ) -> Optional[ConfirmationState]:
        """Get confirmation state for a session."""
        async with self._lock:
            return self._confirmations.get(session_id)

    async def set_confirmation_state(
        self,
        session_id: UUID,
        state: ConfirmationState
    ) -> None:
        """Set confirmation state for a session."""
        async with self._lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session {session_id} not found")
            self._confirmations[session_id] = state


# Singleton session store
_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """
    Get the session store singleton.

    Creates an in-memory store by default.
    Production should override with Redis or database-backed store.

    Returns:
        SessionStore instance
    """
    global _store
    if _store is None:
        settings = get_settings()
        if settings.session_store == "memory":
            _store = InMemorySessionStore()
        else:
            # Future: Add Redis or database store
            _store = InMemorySessionStore()
    return _store


def reset_session_store() -> None:
    """Reset the session store singleton (useful for testing)."""
    global _store
    _store = None


# Convenience functions for session management

async def create_session(user_id: str) -> AgentSession:
    """Create a new session for a user."""
    store = get_session_store()
    return await store.create(user_id)


async def get_session(session_id: UUID) -> Optional[AgentSession]:
    """Get a session by ID."""
    store = get_session_store()
    return await store.get(session_id)


async def update_session(session: AgentSession) -> AgentSession:
    """Update a session."""
    store = get_session_store()
    return await store.update(session)


async def delete_session(session_id: UUID) -> bool:
    """Delete a session."""
    store = get_session_store()
    return await store.delete(session_id)


async def get_session_context(session_id: UUID) -> Optional[ConversationContext]:
    """Get conversation context for a session."""
    store = get_session_store()
    if isinstance(store, InMemorySessionStore):
        return await store.get_context(session_id)
    return None


async def set_session_context(
    session_id: UUID,
    context: ConversationContext
) -> None:
    """Set conversation context for a session."""
    store = get_session_store()
    if isinstance(store, InMemorySessionStore):
        await store.set_context(session_id, context)


async def get_session_confirmation(
    session_id: UUID
) -> Optional[ConfirmationState]:
    """Get confirmation state for a session."""
    store = get_session_store()
    if isinstance(store, InMemorySessionStore):
        return await store.get_confirmation_state(session_id)
    return None


async def set_session_confirmation(
    session_id: UUID,
    state: ConfirmationState
) -> None:
    """Set confirmation state for a session."""
    store = get_session_store()
    if isinstance(store, InMemorySessionStore):
        await store.set_confirmation_state(session_id, state)
