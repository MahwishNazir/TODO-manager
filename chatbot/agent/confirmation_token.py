"""
Confirmation Token Service (Phase III Part 5 - T007).

Provides JWT-based stateless tokens for confirming destructive actions.
Tokens expire after 5 minutes to prevent stale confirmations.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from chatbot.agent.config import get_settings


class ConfirmationTokenService:
    """
    Service for generating and validating confirmation tokens.

    Uses JWT for stateless token management. Each token:
    - Contains the action type and parameters
    - Is bound to a specific user
    - Expires after 5 minutes
    - Is single-use (though enforcement is stateless via expiry)

    This enables the confirmation flow without server-side state.
    """

    # Token expiration time in minutes
    TOKEN_EXPIRY_MINUTES = 5

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize the confirmation token service.

        Args:
            secret_key: JWT signing secret. If not provided, uses
                       BETTER_AUTH_SECRET from settings.
        """
        if secret_key:
            self._secret = secret_key
        else:
            settings = get_settings()
            self._secret = settings.better_auth_secret

    def generate_token(
        self,
        action: str,
        user_id: str,
        description: str,
        **action_params: Any,
    ) -> Dict[str, Any]:
        """
        Generate a confirmation token for a destructive action.

        Args:
            action: Action type (e.g., "delete_task")
            user_id: User requesting the action
            description: Human-readable description of the action
            **action_params: Additional parameters for the action (e.g., task_id)

        Returns:
            PendingConfirmation dict with token, action, description, expires_at
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self.TOKEN_EXPIRY_MINUTES)

        # Build JWT payload
        payload = {
            "jti": str(uuid4()),  # Unique token ID
            "sub": user_id,  # Subject (user)
            "action": action,  # Action type
            "params": action_params,  # Action parameters
            "iat": int(now.timestamp()),  # Issued at
            "exp": int(expires_at.timestamp()),  # Expiration
        }

        # Sign the token
        token = jwt.encode(payload, self._secret, algorithm="HS256")

        return {
            "token": token,
            "action": action,
            "description": description,
            "expires_at": expires_at.isoformat(),
        }

    def validate_token(
        self,
        token: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Validate a confirmation token.

        Args:
            token: The JWT token to validate
            user_id: Expected user ID (must match token subject)

        Returns:
            Dict with validation result:
            - valid: bool indicating if token is valid
            - action: action type (if valid)
            - params: action parameters (if valid)
            - error: error code (if invalid)
            - message: error message (if invalid)

        Error codes:
            - CONFIRMATION_EXPIRED: Token has expired
            - INVALID_CONFIRMATION: Token is malformed or user mismatch
        """
        try:
            # Decode and verify the token
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                options={"require": ["exp", "sub", "action"]},
            )

            # Verify user matches
            if payload.get("sub") != user_id:
                return {
                    "valid": False,
                    "error": "INVALID_CONFIRMATION",
                    "message": "Token was issued for a different user",
                }

            # Token is valid
            return {
                "valid": True,
                "action": payload.get("action"),
                "params": payload.get("params", {}),
            }

        except jwt.ExpiredSignatureError:
            return {
                "valid": False,
                "error": "CONFIRMATION_EXPIRED",
                "message": "Confirmation token has expired. Please request the action again.",
            }

        except jwt.InvalidTokenError as e:
            return {
                "valid": False,
                "error": "INVALID_CONFIRMATION",
                "message": f"Invalid confirmation token: {str(e)}",
            }

    def is_destructive_action(self, action: str) -> bool:
        """
        Check if an action type is considered destructive.

        Args:
            action: The action type to check

        Returns:
            True if the action requires confirmation
        """
        destructive_actions = {
            "delete_task",
            "delete_all_tasks",
            "clear_completed",
        }
        return action in destructive_actions


# Singleton instance
_service: Optional[ConfirmationTokenService] = None


def get_confirmation_service() -> ConfirmationTokenService:
    """Get the singleton confirmation token service."""
    global _service
    if _service is None:
        _service = ConfirmationTokenService()
    return _service
