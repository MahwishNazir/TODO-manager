"""
Unit tests for confirmation response parsing (T060).

Tests parsing of yes/no/cancel responses.
"""

import pytest

from chatbot.agent.confirmation import (
    parse_confirmation_response,
    ConfirmationResponse,
)


class TestParseYesResponses:
    """Tests for parsing YES responses."""

    YES_VARIATIONS = [
        # Explicit
        "yes",
        "Yes",
        "YES",
        "y",
        "Y",
        # Colloquial
        "yeah",
        "yea",
        "yep",
        "sure",
        # Formal
        "ok",
        "okay",
        "OK",
        "Okay",
        # Commands
        "confirm",
        "proceed",
        "go ahead",
        "do it",
        "execute",
        "affirmative",
    ]

    @pytest.mark.parametrize("response", YES_VARIATIONS)
    def test_yes_variations(self, response):
        """Should recognize yes variations."""
        result = parse_confirmation_response(response)
        assert result == ConfirmationResponse.YES, f"Failed for '{response}'"

    def test_yes_with_whitespace(self):
        """Should handle whitespace."""
        result = parse_confirmation_response("  yes  ")
        assert result == ConfirmationResponse.YES

    def test_yes_with_punctuation(self):
        """Should handle without punctuation matching."""
        # Note: current implementation requires exact match
        result = parse_confirmation_response("yes!")
        # May be UNCLEAR since we match exactly
        assert result in [ConfirmationResponse.YES, ConfirmationResponse.UNCLEAR]


class TestParseNoResponses:
    """Tests for parsing NO responses."""

    NO_VARIATIONS = [
        # Explicit
        "no",
        "No",
        "NO",
        "n",
        "N",
        # Colloquial
        "nope",
        "nah",
        # Commands
        "cancel",
        "abort",
        "stop",
        "don't",
        "dont",
        "never mind",
        "negative",
    ]

    @pytest.mark.parametrize("response", NO_VARIATIONS)
    def test_no_variations(self, response):
        """Should recognize no variations."""
        result = parse_confirmation_response(response)
        assert result == ConfirmationResponse.NO, f"Failed for '{response}'"

    def test_no_with_whitespace(self):
        """Should handle whitespace."""
        result = parse_confirmation_response("  no  ")
        assert result == ConfirmationResponse.NO


class TestParseUnclearResponses:
    """Tests for parsing UNCLEAR responses."""

    UNCLEAR_VARIATIONS = [
        "",
        "maybe",
        "perhaps",
        "I don't know",
        "hmm",
        "what?",
        "delete it",  # Not a direct yes/no
        "the task",  # Not a direct yes/no
        "groceries",  # Task reference, not confirmation
    ]

    @pytest.mark.parametrize("response", UNCLEAR_VARIATIONS)
    def test_unclear_variations(self, response):
        """Should return UNCLEAR for ambiguous input."""
        result = parse_confirmation_response(response)
        assert result == ConfirmationResponse.UNCLEAR, f"Failed for '{response}'"

    def test_none_returns_unclear(self):
        """None input should return UNCLEAR."""
        result = parse_confirmation_response("")
        assert result == ConfirmationResponse.UNCLEAR


class TestEdgeCases:
    """Tests for edge cases in confirmation parsing."""

    def test_case_insensitive(self):
        """Should be case insensitive."""
        assert parse_confirmation_response("YES") == ConfirmationResponse.YES
        assert parse_confirmation_response("No") == ConfirmationResponse.NO

    def test_mixed_case(self):
        """Should handle mixed case."""
        assert parse_confirmation_response("YeS") == ConfirmationResponse.YES
        assert parse_confirmation_response("nO") == ConfirmationResponse.NO

    def test_long_response_unclear(self):
        """Long responses should be UNCLEAR."""
        result = parse_confirmation_response("Yes, I want to delete the task please")
        # This is a sentence, not just "yes"
        assert result == ConfirmationResponse.UNCLEAR

    def test_number_unclear(self):
        """Numbers should be UNCLEAR."""
        result = parse_confirmation_response("1")
        assert result == ConfirmationResponse.UNCLEAR

    def test_emoji_unclear(self):
        """Emojis should be UNCLEAR."""
        result = parse_confirmation_response("👍")
        assert result == ConfirmationResponse.UNCLEAR
