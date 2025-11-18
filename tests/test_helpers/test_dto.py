"""
Tests for Datetime Operations (DtO.py) module.

This module contains unit tests for the datetime manipulation utilities.
"""

import pytest
from datetime import datetime, timedelta
from helpers.DtO import parse_datetime, format_datetime, time_since


class TestParseDatetime:
    """Test suite for parse_datetime function."""
    
    def test_parse_default_format(self):
        """Test parsing with default format."""
        result = parse_datetime("2024-01-15 14:30:00")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 0
    
    def test_parse_custom_format(self):
        """Test parsing with custom format."""
        result = parse_datetime("15/01/2024 14:30", fmt="%d/%m/%Y %H:%M")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_date_only(self):
        """Test parsing date only."""
        result = parse_datetime("2024-01-15", fmt="%Y-%m-%d")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_parse_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            parse_datetime("invalid-date-format")
    
    @pytest.mark.parametrize("date_str,fmt,expected_year,expected_month", [
        ("2024-01-15 10:00:00", "%Y-%m-%d %H:%M:%S", 2024, 1),
        ("2023-12-25 00:00:00", "%Y-%m-%d %H:%M:%S", 2023, 12),
        ("2024-06-30 23:59:59", "%Y-%m-%d %H:%M:%S", 2024, 6),
    ])
    def test_various_dates(self, date_str, fmt, expected_year, expected_month):
        """Test parsing various date strings."""
        result = parse_datetime(date_str, fmt)
        assert result.year == expected_year
        assert result.month == expected_month


class TestFormatDatetime:
    """Test suite for format_datetime function."""
    
    def test_format_default(self):
        """Test formatting with default format."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = format_datetime(dt)
        assert result == "2024-01-15 14:30:00"
    
    def test_format_date_only(self):
        """Test formatting date only."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = format_datetime(dt, fmt="%Y-%m-%d")
        assert result == "2024-01-15"
    
    def test_format_time_only(self):
        """Test formatting time only."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = format_datetime(dt, fmt="%H:%M:%S")
        assert result == "14:30:00"
    
    def test_format_custom(self):
        """Test custom formatting."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = format_datetime(dt, fmt="%d/%m/%Y %H:%M")
        assert result == "15/01/2024 14:30"
    
    def test_format_readable(self):
        """Test readable date format."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = format_datetime(dt, fmt="%B %d, %Y at %I:%M %p")
        assert "January 15, 2024" in result
    
    @pytest.mark.parametrize("year,month,day,fmt,expected", [
        (2024, 1, 15, "%Y-%m-%d", "2024-01-15"),
        (2024, 12, 31, "%d/%m/%Y", "31/12/2024"),
        (2024, 6, 1, "%B %Y", "June 2024"),
    ])
    def test_various_formats(self, year, month, day, fmt, expected):
        """Test various format strings."""
        dt = datetime(year, month, day)
        result = format_datetime(dt, fmt)
        assert result == expected


class TestTimeSince:
    """Test suite for time_since function."""
    
    def test_time_since_seconds(self):
        """Test time difference in seconds."""
        past = datetime(2024, 1, 1, 12, 0, 0)
        now = datetime(2024, 1, 1, 12, 0, 30)
        result = time_since(past, now)
        assert "30" in result or "0:00:30" in result
    
    def test_time_since_minutes(self):
        """Test time difference in minutes."""
        past = datetime(2024, 1, 1, 12, 0, 0)
        now = datetime(2024, 1, 1, 12, 15, 0)
        result = time_since(past, now)
        assert "15" in result or "0:15:00" in result
    
    def test_time_since_hours(self):
        """Test time difference in hours."""
        past = datetime(2024, 1, 1, 12, 0, 0)
        now = datetime(2024, 1, 1, 15, 0, 0)
        result = time_since(past, now)
        assert "3" in result or "3:00:00" in result
    
    def test_time_since_days(self):
        """Test time difference in days."""
        past = datetime(2024, 1, 1, 0, 0, 0)
        now = datetime(2024, 1, 2, 0, 0, 0)
        result = time_since(past, now)
        assert "1 day" in result
    
    def test_time_since_multiple_days(self):
        """Test time difference with multiple days."""
        past = datetime(2024, 1, 1, 0, 0, 0)
        now = datetime(2024, 1, 8, 0, 0, 0)
        result = time_since(past, now)
        assert "7 day" in result
    
    def test_time_since_no_now_parameter(self):
        """Test time_since without providing 'now' parameter."""
        # Should use current time
        past = datetime.now() - timedelta(hours=1)
        result = time_since(past)
        # Result should indicate approximately 1 hour
        assert isinstance(result, str)
        # Should be around 1 hour (between 59 minutes and 61 minutes)
        assert "1:00" in result or "0:59" in result or "1:01" in result or "3600" in result
    
    def test_time_since_future_date(self):
        """Test time_since with future date (negative delta)."""
        past = datetime(2024, 1, 2, 0, 0, 0)
        now = datetime(2024, 1, 1, 0, 0, 0)
        result = time_since(past, now)
        # Should return negative timedelta as string
        assert isinstance(result, str)


class TestDatetimeOperationsIntegration:
    """Integration tests for datetime operations."""
    
    def test_parse_format_roundtrip(self):
        """Test parsing and formatting roundtrip."""
        original = "2024-01-15 14:30:00"
        parsed = parse_datetime(original)
        formatted = format_datetime(parsed)
        assert formatted == original
    
    def test_complex_workflow(self):
        """Test complex datetime workflow."""
        # Parse a date string
        date_str = "2024-01-01 00:00:00"
        dt = parse_datetime(date_str)
        
        # Calculate time since
        now = datetime(2024, 1, 2, 12, 0, 0)
        elapsed = time_since(dt, now)
        
        # Format the original datetime
        formatted = format_datetime(dt, "%Y-%m-%d")
        
        assert isinstance(elapsed, str)
        assert formatted == "2024-01-01"
        assert "1 day" in elapsed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
