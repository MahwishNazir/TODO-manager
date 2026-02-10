"""
Unit tests for ChatKit API route (T004, T005).

Tests endpoint registration and configuration.
"""

import pytest
from chatbot.api.main import app


class TestChatKitRoute:
    """Tests for ChatKit API route registration."""

    def test_chatkit_endpoint_registered(self):
        routes = [r.path for r in app.routes]
        assert "/chatkit" in routes

    def test_chatkit_endpoint_accepts_post(self):
        for route in app.routes:
            if hasattr(route, "path") and route.path == "/chatkit":
                assert "POST" in route.methods
                break
        else:
            pytest.fail("/chatkit route not found")

    def test_chatkit_tagged_correctly(self):
        for route in app.routes:
            if hasattr(route, "path") and route.path == "/chatkit":
                assert "chatkit" in route.tags
                break
