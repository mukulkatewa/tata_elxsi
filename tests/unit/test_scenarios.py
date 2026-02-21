"""
Unit tests for scenario application.
"""

import pytest
from autoforge.dashboard.simulation.vehicle_simulator import VehicleSimulator
from autoforge.dashboard.simulation.scenarios import apply_scenario, SCENARIOS


def test_apply_scenario_raises_error_for_invalid_scenario():
    """Test that apply_scenario raises ValueError for unknown scenario names."""
    sim = VehicleSimulator()
    
    with pytest.raises(ValueError) as exc_info:
        apply_scenario(sim, "invalid_scenario_name")
    
    assert "Unknown scenario" in str(exc_info.value)
    assert "invalid_scenario_name" in str(exc_info.value)


def test_apply_scenario_applies_signal_overrides():
    """Test that apply_scenario immediately applies signal_overrides."""
    sim = VehicleSimulator()
    
    # Apply tyre_puncture scenario which sets tyre_pressure_fl to 220.0
    apply_scenario(sim, "tyre_puncture")
    
    # Check that the override was applied
    assert sim.tyre_pressure_fl == 220.0


def test_apply_scenario_stores_signal_trends():
    """Test that apply_scenario stores signal_trends in _scenario_state."""
    sim = VehicleSimulator()
    
    # Apply tyre_puncture scenario
    apply_scenario(sim, "tyre_puncture")
    
    # Check that _scenario_state contains the trends
    assert sim._scenario_state["name"] == "tyre_puncture"
    assert sim._scenario_state["active"] is True
    assert "trends" in sim._scenario_state
    assert "tyre_pressure_fl" in sim._scenario_state["trends"]
    
    # Check the trend values (target_value, ticks_to_reach)
    target_value, ticks = sim._scenario_state["trends"]["tyre_pressure_fl"]
    assert target_value == 80.0
    assert ticks == 30


def test_apply_scenario_sets_active_flag():
    """Test that apply_scenario sets the active flag in _scenario_state."""
    sim = VehicleSimulator()
    
    # Initially not active
    assert sim._scenario_state.get("active", False) is False
    
    # Apply scenario
    apply_scenario(sim, "overheating")
    
    # Should now be active
    assert sim._scenario_state["active"] is True


def test_apply_scenario_records_start_tick():
    """Test that apply_scenario records the current tick count."""
    sim = VehicleSimulator()
    
    # Advance some ticks
    sim.tick()
    sim.tick()
    sim.tick()
    
    current_tick = sim._tick_count
    
    # Apply scenario
    apply_scenario(sim, "highway_cruise")
    
    # Should record the tick count
    assert sim._scenario_state["start_tick"] == current_tick


def test_apply_scenario_highway_cruise_overrides():
    """Test that highway_cruise scenario applies multiple overrides."""
    sim = VehicleSimulator()
    
    # Apply highway_cruise scenario
    apply_scenario(sim, "highway_cruise")
    
    # Check all overrides were applied
    assert sim.vehicle_speed == 120.0
    assert sim.gear_position == 6
    assert sim.throttle_position == 40.0
    assert sim.brake_position == 0.0


def test_apply_scenario_low_battery_no_overrides():
    """Test that low_battery scenario works with no signal_overrides."""
    sim = VehicleSimulator()
    
    # Record initial values
    initial_speed = sim.vehicle_speed
    initial_battery = sim.battery_soc
    
    # Apply low_battery scenario (has no overrides, only trends)
    apply_scenario(sim, "low_battery")
    
    # Values should not change immediately (no overrides)
    assert sim.vehicle_speed == initial_speed
    assert sim.battery_soc == initial_battery
    
    # But trends should be stored
    assert "battery_soc" in sim._scenario_state["trends"]


def test_apply_scenario_normal_clears_trends():
    """Test that applying normal scenario clears trends."""
    sim = VehicleSimulator()
    
    # Apply a scenario with trends
    apply_scenario(sim, "tyre_puncture")
    assert len(sim._scenario_state["trends"]) > 0
    
    # Apply normal scenario
    apply_scenario(sim, "normal")
    
    # Trends should be empty
    assert len(sim._scenario_state["trends"]) == 0
    assert sim._scenario_state["name"] == "normal"


def test_apply_scenario_all_scenarios_valid():
    """Test that all scenarios in SCENARIOS can be applied without error."""
    for scenario_name in SCENARIOS.keys():
        sim = VehicleSimulator()
        
        # Should not raise any exception
        apply_scenario(sim, scenario_name)
        
        # Should set the scenario name
        assert sim._scenario_state["name"] == scenario_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
