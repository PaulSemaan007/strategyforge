"""
Tests for geospatial calculations.

These tests verify the accuracy of distance and bearing calculations
used by agents for military planning.
"""

import pytest
from src.geo.distance import (
    calculate_distance,
    calculate_bearing,
    cardinal_direction,
    is_within_range,
    taiwan_strait_width
)


class TestDistanceCalculations:
    """Test suite for distance calculations."""

    def test_same_point_zero_distance(self):
        """Distance from a point to itself should be zero."""
        pos = (25.0, 121.0)
        assert calculate_distance(pos, pos) == 0.0

    def test_taipei_to_xiamen(self):
        """Verify Taiwan Strait crossing distance."""
        taipei = (25.0330, 121.5654)
        xiamen = (24.4798, 118.0894)

        dist = calculate_distance(taipei, xiamen)

        # Should be approximately 330-340 km
        assert 320 < dist < 350

    def test_taiwan_strait_width(self):
        """Verify strait width at narrowest point."""
        width = taiwan_strait_width()

        # Narrowest point is approximately 130 km
        assert 120 < width < 140

    def test_known_distance_london_paris(self):
        """Test against known London-Paris distance (~344 km)."""
        london = (51.5074, -0.1278)
        paris = (48.8566, 2.3522)

        dist = calculate_distance(london, paris)

        # Should be approximately 344 km
        assert 340 < dist < 350


class TestBearingCalculations:
    """Test suite for bearing calculations."""

    def test_due_north(self):
        """Moving due north should have bearing ~0°."""
        start = (24.0, 121.0)
        end = (25.0, 121.0)  # Same longitude, higher latitude

        bearing = calculate_bearing(start, end)

        assert bearing < 5 or bearing > 355  # Near 0°

    def test_due_east(self):
        """Moving due east should have bearing ~90°."""
        start = (24.0, 120.0)
        end = (24.0, 121.0)  # Same latitude, higher longitude

        bearing = calculate_bearing(start, end)

        assert 85 < bearing < 95  # Near 90°

    def test_due_south(self):
        """Moving due south should have bearing ~180°."""
        start = (25.0, 121.0)
        end = (24.0, 121.0)

        bearing = calculate_bearing(start, end)

        assert 175 < bearing < 185  # Near 180°


class TestCardinalDirections:
    """Test conversion of bearings to cardinal directions."""

    @pytest.mark.parametrize("bearing,expected", [
        (0, "N"),
        (45, "NE"),
        (90, "E"),
        (135, "SE"),
        (180, "S"),
        (225, "SW"),
        (270, "W"),
        (315, "NW"),
        (360, "N"),
    ])
    def test_cardinal_directions(self, bearing, expected):
        """Test all eight cardinal directions."""
        assert cardinal_direction(bearing) == expected


class TestRangeChecks:
    """Test weapon range calculations."""

    def test_target_in_range(self):
        """Target within range should return True."""
        unit = (24.5, 120.0)
        target = (24.6, 120.1)
        range_km = 50

        assert is_within_range(unit, target, range_km) is True

    def test_target_out_of_range(self):
        """Target outside range should return False."""
        unit = (24.5, 120.0)
        target = (25.5, 121.0)  # ~140 km away
        range_km = 50

        assert is_within_range(unit, target, range_km) is False

    def test_target_at_exact_range(self):
        """Target at exactly max range should return True."""
        unit = (24.0, 120.0)
        target = (24.0, 121.0)  # ~100 km east

        dist = calculate_distance(unit, target)

        # Set range to exact distance
        assert is_within_range(unit, target, dist) is True


class TestScenarioSpecificCalculations:
    """Test calculations specific to wargame scenarios."""

    def test_fighter_intercept_feasibility(self):
        """
        Test if a fighter can intercept a target.

        Scenario: Blue fighter at Taiwan, Red bomber approaching from mainland.
        Fighter speed: 2000 km/h, needs to intercept before bomber reaches coast.
        """
        fighter_pos = (25.0, 121.0)  # Taiwan
        bomber_pos = (25.0, 119.0)   # Over strait

        dist = calculate_distance(fighter_pos, bomber_pos)
        fighter_time_hours = dist / 2000  # 2000 km/h

        # Fighter should reach bomber position in under 10 minutes
        assert fighter_time_hours < (10 / 60)  # 10 minutes in hours

    def test_naval_transit_time_estimate(self):
        """
        Verify naval transit time across Taiwan Strait.

        A destroyer at 50 km/h should cross ~180 km strait in ~3.6 hours.
        """
        west_strait = (24.5, 119.0)
        east_strait = (24.5, 120.5)

        dist = calculate_distance(west_strait, east_strait)
        transit_hours = dist / 50  # 50 km/h

        # Should take 3-4 hours
        assert 3 < transit_hours < 4.5
