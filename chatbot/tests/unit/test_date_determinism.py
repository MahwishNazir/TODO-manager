"""
Unit tests for date interpretation determinism (T107).

Tests that date parsing is consistent and deterministic (FR-060 to FR-063).
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import List

from chatbot.agent.utils.date_parser import (
    parse_relative_date,
    parse_date_expression,
    format_date_for_display,
)


class TestTomorrowDeterminism:
    """Tests that 'tomorrow' always means the next calendar day."""

    @pytest.fixture
    def reference_dates(self) -> List[datetime]:
        """Various reference dates across different scenarios."""
        return [
            # Regular weekdays
            datetime(2024, 3, 18, 10, 0, tzinfo=timezone.utc),  # Monday
            datetime(2024, 3, 19, 14, 30, tzinfo=timezone.utc),  # Tuesday afternoon
            datetime(2024, 3, 22, 23, 59, tzinfo=timezone.utc),  # Friday late night
            # Weekend
            datetime(2024, 3, 23, 8, 0, tzinfo=timezone.utc),  # Saturday
            datetime(2024, 3, 24, 16, 0, tzinfo=timezone.utc),  # Sunday
            # Month boundaries
            datetime(2024, 3, 31, 12, 0, tzinfo=timezone.utc),  # End of March
            datetime(2024, 2, 28, 12, 0, tzinfo=timezone.utc),  # Feb 28 (leap year)
            datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc),  # Feb 29 (leap year)
            # Year boundary
            datetime(2024, 12, 31, 12, 0, tzinfo=timezone.utc),  # New Year's Eve
        ]

    def test_tomorrow_is_always_next_day(self, reference_dates):
        """'tomorrow' should always be exactly 1 day after reference date."""
        for ref_date in reference_dates:
            result = parse_relative_date("tomorrow", ref_date)

            expected = ref_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

            assert result == expected, f"Failed for reference date: {ref_date}"

    def test_tomorrow_case_insensitive(self):
        """'tomorrow' should work regardless of case."""
        ref_date = datetime(2024, 3, 18, 10, 0, tzinfo=timezone.utc)
        expected = datetime(2024, 3, 19, 0, 0, tzinfo=timezone.utc)

        variations = ["tomorrow", "TOMORROW", "Tomorrow", "ToMoRrOw"]
        for variation in variations:
            result = parse_relative_date(variation, ref_date)
            assert result == expected, f"Failed for variation: {variation}"

    def test_tomorrow_at_month_boundary(self):
        """'tomorrow' on last day of month should go to next month."""
        ref_date = datetime(2024, 3, 31, 12, 0, tzinfo=timezone.utc)
        result = parse_relative_date("tomorrow", ref_date)

        assert result.month == 4
        assert result.day == 1
        assert result.year == 2024

    def test_tomorrow_at_year_boundary(self):
        """'tomorrow' on Dec 31 should go to Jan 1 of next year."""
        ref_date = datetime(2024, 12, 31, 12, 0, tzinfo=timezone.utc)
        result = parse_relative_date("tomorrow", ref_date)

        assert result.month == 1
        assert result.day == 1
        assert result.year == 2025

    def test_tomorrow_leap_year(self):
        """'tomorrow' on Feb 28 of leap year should go to Feb 29."""
        ref_date = datetime(2024, 2, 28, 12, 0, tzinfo=timezone.utc)
        result = parse_relative_date("tomorrow", ref_date)

        assert result.month == 2
        assert result.day == 29
        assert result.year == 2024


class TestTodayDeterminism:
    """Tests that 'today' always means the current calendar day."""

    def test_today_same_date(self):
        """'today' should return the same date as reference."""
        ref_date = datetime(2024, 3, 18, 14, 30, tzinfo=timezone.utc)
        result = parse_relative_date("today", ref_date)

        assert result.year == 2024
        assert result.month == 3
        assert result.day == 18
        assert result.hour == 0
        assert result.minute == 0

    def test_today_normalized_to_midnight(self):
        """'today' should always be normalized to midnight."""
        ref_date = datetime(2024, 3, 18, 23, 59, 59, tzinfo=timezone.utc)
        result = parse_relative_date("today", ref_date)

        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0


class TestNextWeekDeterminism:
    """Tests that 'next week' always means exactly 7 days."""

    def test_next_week_always_7_days(self):
        """'next week' should always be exactly 7 days ahead."""
        test_cases = [
            datetime(2024, 3, 18, tzinfo=timezone.utc),  # Monday
            datetime(2024, 3, 23, tzinfo=timezone.utc),  # Saturday
            datetime(2024, 3, 24, tzinfo=timezone.utc),  # Sunday
        ]

        for ref_date in test_cases:
            result = parse_relative_date("next week", ref_date)
            expected = ref_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7)
            assert result == expected, f"Failed for {ref_date}"

    def test_in_a_week_same_as_next_week(self):
        """'in a week' should be identical to 'next week'."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)

        next_week = parse_relative_date("next week", ref_date)
        in_a_week = parse_relative_date("in a week", ref_date)

        assert next_week == in_a_week


class TestNextDayNameDeterminism:
    """Tests that 'next <dayname>' is consistent."""

    @pytest.mark.parametrize("day_name,weekday_num", [
        ("monday", 0),
        ("tuesday", 1),
        ("wednesday", 2),
        ("thursday", 3),
        ("friday", 4),
        ("saturday", 5),
        ("sunday", 6),
    ])
    def test_next_day_always_in_future(self, day_name, weekday_num):
        """'next <day>' should always return a future date."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)  # Monday
        result = parse_relative_date(f"next {day_name}", ref_date)

        assert result > ref_date.replace(hour=0, minute=0, second=0, microsecond=0)

    def test_next_day_when_same_day(self):
        """'next monday' on Monday should return next week's Monday."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)  # Monday
        result = parse_relative_date("next monday", ref_date)

        # Should be exactly 7 days later
        assert result.day == 25
        assert result.month == 3

    def test_next_day_when_different_day(self):
        """'next friday' on Monday should return this week's Friday."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)  # Monday
        result = parse_relative_date("next friday", ref_date)

        # Friday is 4 days after Monday
        assert result.day == 22
        assert result.month == 3


class TestInXDaysDeterminism:
    """Tests that 'in X days' is consistent."""

    @pytest.mark.parametrize("days", [1, 2, 3, 5, 7, 10, 30, 100])
    def test_in_x_days_exact_offset(self, days):
        """'in X days' should add exactly X days."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)
        result = parse_relative_date(f"in {days} days", ref_date)

        expected = ref_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days)
        assert result == expected

    def test_in_1_day_same_as_tomorrow(self):
        """'in 1 day' should be identical to 'tomorrow'."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)

        tomorrow = parse_relative_date("tomorrow", ref_date)
        in_1_day = parse_relative_date("in 1 day", ref_date)

        assert tomorrow == in_1_day


class TestRepeatedCallsDeterminism:
    """Tests that repeated calls produce identical results."""

    def test_same_input_same_output(self):
        """Same input should always produce same output."""
        ref_date = datetime(2024, 3, 18, 12, 0, tzinfo=timezone.utc)
        expressions = [
            "tomorrow",
            "today",
            "next week",
            "next friday",
            "in 5 days",
        ]

        for expr in expressions:
            results = [parse_relative_date(expr, ref_date) for _ in range(10)]
            first_result = results[0]
            assert all(r == first_result for r in results), f"Inconsistent results for: {expr}"

    def test_expression_extraction_consistent(self):
        """parse_date_expression should consistently extract dates."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)
        text = "Buy groceries tomorrow for the party"

        results = [parse_date_expression(text, ref_date) for _ in range(10)]
        first_date, first_text = results[0]

        for date, text in results:
            assert date == first_date
            assert text == first_text


class TestDateExtractionDeterminism:
    """Tests for deterministic date extraction from text."""

    def test_extract_tomorrow_from_text(self):
        """Should extract 'tomorrow' from various sentence structures."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)
        test_cases = [
            ("Do this tomorrow", "Do this"),
            ("Tomorrow: finish report", "finish report"),
            ("Call mom tomorrow afternoon", "Call mom afternoon"),
        ]

        for input_text, expected_remaining in test_cases:
            date, remaining = parse_date_expression(input_text, ref_date)
            assert date is not None
            assert date.day == 19
            # Check remaining text is cleaned up
            assert "tomorrow" not in remaining.lower()

    def test_extract_next_week_from_text(self):
        """Should extract 'next week' from text."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)
        date, remaining = parse_date_expression("Submit report next week", ref_date)

        assert date is not None
        assert date.day == 25  # 7 days after March 18
        assert "next week" not in remaining.lower()


class TestFormatDateDeterminism:
    """Tests for deterministic date formatting."""

    def test_format_today_consistent(self):
        """'today' should format consistently."""
        # Note: This test uses current time, so we verify format is stable
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        results = [format_date_for_display(today) for _ in range(5)]

        assert all(r == "today" for r in results)

    def test_format_tomorrow_consistent(self):
        """'tomorrow' should format consistently."""
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        results = [format_date_for_display(tomorrow) for _ in range(5)]

        assert all(r == "tomorrow" for r in results)


class TestEdgeCases:
    """Edge case tests for date parsing."""

    def test_empty_string_returns_none(self):
        """Empty string should return None."""
        assert parse_relative_date("") is None
        assert parse_relative_date("   ") is None

    def test_unrecognized_expression_returns_none(self):
        """Unrecognized expressions should return None."""
        assert parse_relative_date("random text") is None
        assert parse_relative_date("in about a week") is None  # Not exact pattern
        assert parse_relative_date("maybe tomorrow") is None  # Has qualifier

    def test_whitespace_handling(self):
        """Whitespace should be handled consistently."""
        ref_date = datetime(2024, 3, 18, tzinfo=timezone.utc)

        assert parse_relative_date("  tomorrow  ", ref_date) == parse_relative_date("tomorrow", ref_date)
        assert parse_relative_date("next   monday", ref_date) == parse_relative_date("next monday", ref_date)
