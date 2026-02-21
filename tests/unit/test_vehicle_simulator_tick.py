"""
Unit tests for VehicleSimulator tick method.
"""

import pytest
from autoforge.dashboard.simulation.vehicle_simulator import VehicleSimulator


def test_tick_increments_tick_count():
    """Test that tick increments the internal tick counter."""
    sim = VehicleSimulator()
    initial_count = sim._tick_count
    sim.tick()
    assert sim._tick_count == initial_count + 1


def test_tick_returns_complete_signal_dictionary():
    """Test that tick returns all 13 VSS signal keys."""
    sim = VehicleSimulator()
    result = sim.tick()
    
    expected_keys = {
        "vehicle_speed",
        "tyre_pressure_fl",
        "tyre_pressure_fr",
        "tyre_pressure_rl",
        "tyre_pressure_rr",
        "battery_soc",
        "ev_range",
        "throttle_position",
        "brake_position",
        "gear_position",
        "steering_angle",
        "motor_temperature",
        "coolant_temperature",
    }
    
    assert set(result.keys()) == expected_keys


def test_tick_returns_numeric_values():
    """Test that all returned values are numeric."""
    sim = VehicleSimulator()
    result = sim.tick()
    
    for key, value in result.items():
        assert isinstance(value, (int, float)), f"{key} should be numeric"


def test_tick_clamps_values_to_valid_ranges():
    """Test that tick clamps signal values to their valid ranges."""
    sim = VehicleSimulator()
    
    # Set extreme values
    sim.vehicle_speed = 250.0  # Above max
    sim.tyre_pressure_fl = 400.0  # Above max
    sim.battery_soc = 110.0  # Above max
    sim.motor_temperature = 150.0  # Above max
    
    result = sim.tick()
    
    # Check clamping
    assert 0.0 <= result["vehicle_speed"] <= 200.0
    assert 150.0 <= result["tyre_pressure_fl"] <= 350.0
    assert 0.0 <= result["battery_soc"] <= 100.0
    assert 20.0 <= result["motor_temperature"] <= 120.0


def test_tick_applies_battery_drain():
    """Test that battery drains by approximately 0.05% per tick in normal mode."""
    sim = VehicleSimulator()
    initial_soc = sim.battery_soc
    
    result = sim.tick()
    
    # Battery should have drained
    assert result["battery_soc"] < initial_soc
    # Should be approximately 0.05% less (allowing for floating point precision)
    assert abs((initial_soc - result["battery_soc"]) - 0.05) < 0.01


def test_tick_updates_ev_range_based_on_battery():
    """Test that ev_range is updated based on battery_soc."""
    sim = VehicleSimulator()
    sim.battery_soc = 80.0
    sim.gear_position = 4  # Normal gear for 1.0x factor
    sim.vehicle_speed = 60.0  # Normal speed for 1.0x factor
    
    result = sim.tick()
    
    # ev_range should be approximately battery_soc * 5.0 (with gear/speed adjustments)
    # For gear 4 and speed 60, factors are both 1.0
    expected_range = result["battery_soc"] * 5.0
    assert abs(result["ev_range"] - expected_range) < 10.0  # Allow some tolerance


def test_tick_gear_affects_range():
    """Test that gear_position affects ev_range calculation."""
    sim = VehicleSimulator()
    sim.battery_soc = 80.0
    sim.vehicle_speed = 60.0
    
    # Test with low gear (less efficient)
    sim.gear_position = 1
    result_low_gear = sim.tick()
    range_low_gear = result_low_gear["ev_range"]
    
    # Reset and test with high gear (more efficient)
    sim.battery_soc = 80.0
    sim.gear_position = 6
    result_high_gear = sim.tick()
    range_high_gear = result_high_gear["ev_range"]
    
    # Higher gear should give better range
    assert range_high_gear > range_low_gear


def test_tick_speed_affects_range():
    """Test that vehicle_speed affects ev_range calculation."""
    sim = VehicleSimulator()
    sim.battery_soc = 80.0
    sim.gear_position = 4
    
    # Test with normal speed
    sim.vehicle_speed = 60.0
    result_normal = sim.tick()
    range_normal = result_normal["ev_range"]
    
    # Reset and test with high speed (less efficient)
    sim.battery_soc = 80.0
    sim.vehicle_speed = 140.0
    result_high = sim.tick()
    range_high = result_high["ev_range"]
    
    # High speed should give worse range
    assert range_high < range_normal


def test_tick_normal_mode_bounded_updates():
    """Test that normal mode updates are within specified bounds."""
    sim = VehicleSimulator()
    
    # Record initial values
    initial_speed = sim.vehicle_speed
    initial_pressure_fl = sim.tyre_pressure_fl
    initial_battery = sim.battery_soc
    
    result = sim.tick()
    
    # Check speed change is within ±5 kmh (plus the random walk)
    speed_change = abs(result["vehicle_speed"] - initial_speed)
    assert speed_change <= 5.0, f"Speed changed by {speed_change} kmh, expected ≤5"
    
    # Check tyre pressure change is within ±1 kPa
    pressure_change = abs(result["tyre_pressure_fl"] - initial_pressure_fl)
    assert pressure_change <= 1.0, f"Pressure changed by {pressure_change} kPa, expected ≤1"
    
    # Check battery drain is approximately 0.05%
    battery_change = initial_battery - result["battery_soc"]
    assert 0 <= battery_change <= 0.1, f"Battery changed by {battery_change}%, expected ~0.05"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
