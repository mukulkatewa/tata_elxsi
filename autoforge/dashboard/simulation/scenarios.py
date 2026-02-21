"""
Fault Scenario Definitions for AutoForge Live Dashboard.

This module provides scenario definitions that simulate various vehicle
fault conditions and driving patterns for demonstration purposes.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class ScenarioDefinition:
    """
    Definition of a fault scenario or driving pattern.
    
    Attributes:
        name: Scenario identifier
        description: Human-readable description of the scenario
        signal_overrides: Immediate value changes applied at tick 0 (signal -> value)
        signal_trends: Progressive changes over time (signal -> (target_value, ticks_to_reach))
    """
    name: str
    description: str
    signal_overrides: Dict[str, float]
    signal_trends: Dict[str, Tuple[float, int]]


# Scenario definitions dictionary
SCENARIOS: Dict[str, ScenarioDefinition] = {
    "normal": ScenarioDefinition(
        name="normal",
        description="Baseline driving with no faults - normal operation",
        signal_overrides={},
        signal_trends={}
    ),
    
    "tyre_puncture": ScenarioDefinition(
        name="tyre_puncture",
        description="Front-left tyre puncture - pressure drops from 220 to 80 kPa over 30 ticks",
        signal_overrides={
            "tyre_pressure_fl": 220.0  # Start at normal pressure
        },
        signal_trends={
            "tyre_pressure_fl": (80.0, 30)  # Drop to 80 kPa over 30 ticks
        }
    ),
    
    "low_battery": ScenarioDefinition(
        name="low_battery",
        description="Battery drains 3x faster than normal - accelerated discharge",
        signal_overrides={},
        signal_trends={
            "battery_soc": (-0.15, 1)  # Triple drain rate: -0.15% per tick instead of -0.05%
        }
    ),
    
    "overheating": ScenarioDefinition(
        name="overheating",
        description="Motor overheating - temperature climbs from 80 to 118°C over 20 ticks",
        signal_overrides={
            "motor_temperature": 80.0  # Start at normal operating temperature
        },
        signal_trends={
            "motor_temperature": (118.0, 20)  # Climb to critical temperature over 20 ticks
        }
    ),
    
    "highway_cruise": ScenarioDefinition(
        name="highway_cruise",
        description="Highway cruise control - speed stays at 120 kmh with minimal variation",
        signal_overrides={
            "vehicle_speed": 120.0,
            "gear_position": 6,  # High gear for highway
            "throttle_position": 40.0,
            "brake_position": 0.0
        },
        signal_trends={
            "vehicle_speed": (120.0, 1)  # Maintain 120 kmh (±2 kmh variation)
        }
    ),
    
    "city_driving": ScenarioDefinition(
        name="city_driving",
        description="City driving pattern - speed oscillates between 0-60 kmh with frequent braking",
        signal_overrides={
            "vehicle_speed": 0.0,
            "gear_position": 2  # Low gear for city
        },
        signal_trends={
            "vehicle_speed": (60.0, 15)  # Oscillate 0-60 kmh with 15-tick period
        }
    )
}


def apply_scenario(simulator, scenario_name: str) -> None:
    """
    Apply a scenario to a VehicleSimulator instance.
    
    This function:
    1. Looks up the scenario in the SCENARIOS dictionary
    2. Applies signal_overrides immediately to the simulator's signal values
    3. Stores signal_trends in the simulator's _scenario_state for progressive updates
    
    Args:
        simulator: VehicleSimulator instance to apply the scenario to
        scenario_name: Name of the scenario to apply (must exist in SCENARIOS)
    
    Raises:
        ValueError: If scenario_name is not found in SCENARIOS dictionary
    """
    # Look up the scenario in the SCENARIOS dictionary
    if scenario_name not in SCENARIOS:
        valid_scenarios = ", ".join(SCENARIOS.keys())
        raise ValueError(
            f"Unknown scenario '{scenario_name}'. "
            f"Valid scenarios are: {valid_scenarios}"
        )
    
    scenario = SCENARIOS[scenario_name]
    
    # Apply signal_overrides immediately to the simulator's signal values
    for signal_name, value in scenario.signal_overrides.items():
        if hasattr(simulator, signal_name):
            setattr(simulator, signal_name, value)
    
    # Store signal_trends in the simulator's _scenario_state for progressive updates
    simulator._scenario_state = {
        "name": scenario_name,
        "active": True,
        "trends": scenario.signal_trends.copy(),
        "start_tick": simulator._tick_count
    }
