"""
Unit tests for VehicleSimulator scenario methods (task 5.3).
Tests trigger_scenario, reset, and scenario progression logic.
"""

import pytest
from autoforge.dashboard.simulation.vehicle_simulator import VehicleSimulator


def test_trigger_scenario_applies_scenario():
    """Test that trigger_scenario applies a scenario correctly."""
    sim = VehicleSimulator()
    
    # Trigger tyre_puncture scenario
    sim.trigger_scenario("tyre_puncture")
    
    # Check that scenario state is active
    assert sim._scenario_state["active"] is True
    assert sim._scenario_state["name"] == "tyre_puncture"
    assert "trends" in sim._scenario_state
    
    # Check that tyre_pressure_fl was set to 220.0 (signal_override)
    assert sim.tyre_pressure_fl == 220.0


def test_trigger_scenario_invalid_name_raises_error():
    """Test that invalid scenario names raise ValueError."""
    sim = VehicleSimulator()
    
    with pytest.raises(ValueError) as exc_info:
        sim.trigger_scenario("invalid_scenario")
    
    assert "Unknown scenario" in str(exc_info.value)
    assert "invalid_scenario" in str(exc_info.value)


def test_trigger_scenario_overheating():
    """Test that overheating scenario is applied correctly."""
    sim = VehicleSimulator()
    
    sim.trigger_scenario("overheating")
    
    # Check scenario state
    assert sim._scenario_state["active"] is True
    assert sim._scenario_state["name"] == "overheating"
    
    # Check that motor_temperature was set to 80.0 (signal_override)
    assert sim.motor_temperature == 80.0


def test_trigger_scenario_low_battery():
    """Test that low_battery scenario is applied correctly."""
    sim = VehicleSimulator()
    
    sim.trigger_scenario("low_battery")
    
    # Check scenario state
    assert sim._scenario_state["active"] is True
    assert sim._scenario_state["name"] == "low_battery"
    
    # low_battery has no signal_overrides, only trends
    assert "trends" in sim._scenario_state


def test_scenario_progression_tyre_puncture():
    """Test that tyre_puncture scenario progresses deterministically."""
    sim = VehicleSimulator()
    
    # Trigger tyre_puncture: 220 -> 80 kPa over 30 ticks
    sim.trigger_scenario("tyre_puncture")
    
    initial_pressure = sim.tyre_pressure_fl
    assert initial_pressure == 220.0
    
    # Run 10 ticks
    for _ in range(10):
        sim.tick()
    
    # After 10 ticks, pressure should have decreased
    pressure_after_10 = sim.tyre_pressure_fl
    assert pressure_after_10 < initial_pressure
    assert pressure_after_10 > 80.0  # Not at target yet
    
    # Run 20 more ticks (total 30)
    for _ in range(20):
        sim.tick()
    
    # After 30 ticks, pressure should be at or very close to 80 kPa
    final_pressure = sim.tyre_pressure_fl
    assert abs(final_pressure - 80.0) < 2.0, f"Expected ~80 kPa, got {final_pressure:.1f} kPa"


def test_scenario_progression_overheating():
    """Test that overheating scenario progresses deterministically."""
    sim = VehicleSimulator()
    
    # Trigger overheating: 80 -> 118 C over 20 ticks
    sim.trigger_scenario("overheating")
    
    initial_temp = sim.motor_temperature
    assert initial_temp == 80.0
    
    # Run 10 ticks
    for _ in range(10):
        sim.tick()
    
    # After 10 ticks, temperature should have increased
    temp_after_10 = sim.motor_temperature
    assert temp_after_10 > initial_temp
    assert temp_after_10 < 118.0  # Not at target yet
    
    # Run 10 more ticks (total 20)
    for _ in range(10):
        sim.tick()
    
    # After 20 ticks, temperature should be at or very close to 118 C
    final_temp = sim.motor_temperature
    assert abs(final_temp - 118.0) < 2.0, f"Expected ~118 C, got {final_temp:.1f} C"


def test_scenario_progression_low_battery():
    """Test that low_battery scenario increases drain rate."""
    sim = VehicleSimulator()
    
    # Set initial battery level
    sim.battery_soc = 50.0
    
    # Trigger low_battery scenario (triple drain rate)
    sim.trigger_scenario("low_battery")
    
    initial_soc = sim.battery_soc
    
    # Run 10 ticks
    for _ in range(10):
        sim.tick()
    
    final_soc = sim.battery_soc
    drain = initial_soc - final_soc
    
    # With triple drain rate, drain should be significantly more than normal 0.5% (0.05 * 10)
    # Expected approximately 1.5% (0.15 * 10), but due to progressive calculation it may vary
    assert drain > 0.8, f"Expected drain > 0.8%, got {drain:.2f}%"


def test_scenario_progression_highway_cruise():
    """Test that highway_cruise scenario maintains speed."""
    sim = VehicleSimulator()
    
    # Trigger highway_cruise: maintain 120 kmh
    sim.trigger_scenario("highway_cruise")
    
    # Check initial state
    assert sim.vehicle_speed == 120.0
    assert sim.gear_position == 6
    
    # Run 10 ticks
    speeds = []
    for _ in range(10):
        result = sim.tick()
        speeds.append(result["vehicle_speed"])
    
    # All speeds should be close to 120 kmh (allowing for small variations)
    for speed in speeds:
        assert abs(speed - 120.0) < 5.0, f"Speed {speed:.1f} too far from 120 kmh"


def test_reset_clears_scenario_state():
    """Test that reset clears scenario state."""
    sim = VehicleSimulator()
    
    # Trigger a scenario
    sim.trigger_scenario("overheating")
    assert sim._scenario_state["active"] is True
    
    # Reset
    sim.reset()
    
    # Check that scenario state is cleared
    assert sim._scenario_state["active"] is False
    assert sim._scenario_state["name"] == "normal"


def test_reset_resets_tick_count():
    """Test that reset resets tick count to 0."""
    sim = VehicleSimulator()
    
    # Run some ticks
    for _ in range(10):
        sim.tick()
    
    assert sim._tick_count > 0
    
    # Reset
    sim.reset()
    
    # Check that tick count is reset
    assert sim._tick_count == 0


def test_reset_reinitializes_signals():
    """Test that reset reinitializes all signals to default values."""
    sim = VehicleSimulator()
    
    # Modify signals
    sim.vehicle_speed = 150.0
    sim.tyre_pressure_fl = 100.0
    sim.battery_soc = 20.0
    sim.motor_temperature = 110.0
    
    # Reset
    sim.reset()
    
    # Check that signals are reset to defaults
    assert sim.vehicle_speed == 60.0
    assert sim.tyre_pressure_fl == 220.0
    assert sim.tyre_pressure_fr == 220.0
    assert sim.tyre_pressure_rl == 220.0
    assert sim.tyre_pressure_rr == 220.0
    assert sim.battery_soc == 85.0
    assert sim.ev_range == 425.0
    assert sim.throttle_position == 30.0
    assert sim.brake_position == 0.0
    assert sim.gear_position == 4
    assert sim.steering_angle == 0.0
    assert sim.motor_temperature == 80.0
    assert sim.coolant_temperature == 75.0


def test_reset_after_scenario_progression():
    """Test that reset works correctly after scenario has progressed."""
    sim = VehicleSimulator()
    
    # Trigger scenario and run some ticks
    sim.trigger_scenario("tyre_puncture")
    for _ in range(15):
        sim.tick()
    
    # Pressure should have decreased
    assert sim.tyre_pressure_fl < 220.0
    
    # Reset
    sim.reset()
    
    # Check that everything is back to defaults
    assert sim.tyre_pressure_fl == 220.0
    assert sim._scenario_state["active"] is False
    assert sim._tick_count == 0


def test_scenario_progression_non_trend_signals_vary():
    """Test that non-trend signals still vary during scenario mode."""
    sim = VehicleSimulator()
    
    # Trigger tyre_puncture (only affects tyre_pressure_fl)
    sim.trigger_scenario("tyre_puncture")
    
    initial_temp = sim.motor_temperature
    
    # Run several ticks
    temps = []
    for _ in range(20):
        sim.tick()
        temps.append(sim.motor_temperature)
    
    # Motor temperature should vary (not all the same)
    assert len(set(temps)) > 1, "Motor temperature should vary during scenario"
    
    # But variations should be smaller than normal mode
    temp_changes = [abs(temps[i] - temps[i-1]) for i in range(1, len(temps))]
    max_change = max(temp_changes)
    assert max_change < 1.0, f"Temperature changes should be small, got {max_change:.2f}"


def test_scenario_progression_after_completion():
    """Test that scenario continues to hold target value after completion."""
    sim = VehicleSimulator()
    
    # Trigger tyre_puncture: 220 -> 80 kPa over 30 ticks
    sim.trigger_scenario("tyre_puncture")
    
    # Run 30 ticks to complete scenario
    for _ in range(30):
        sim.tick()
    
    pressure_at_30 = sim.tyre_pressure_fl
    
    # Run 10 more ticks
    for _ in range(10):
        sim.tick()
    
    pressure_at_40 = sim.tyre_pressure_fl
    
    # Pressure should remain at target (80 kPa)
    assert abs(pressure_at_30 - 80.0) < 2.0
    assert abs(pressure_at_40 - 80.0) < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
