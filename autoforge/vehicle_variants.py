"""
Vehicle Variant Configuration for AutoForge.

Defines vehicle types (ICE, Hybrid, EV) with their specific signal sets,
thresholds, and characteristics.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class VehicleVariant:
    """Configuration for a specific vehicle variant."""
    name: str
    variant_type: str  # ICE, Hybrid, EV
    description: str
    available_signals: List[str]
    signal_defaults: Dict[str, float]
    thresholds: Dict[str, Dict[str, float]]
    features: List[str]


# Vehicle variant definitions
VEHICLE_VARIANTS: Dict[str, VehicleVariant] = {
    "ev": VehicleVariant(
        name="Electric Vehicle",
        variant_type="EV",
        description="Full battery-electric vehicle with regenerative braking",
        available_signals=[
            "vehicle_speed", "battery_soc", "ev_range",
            "tyre_pressure_fl", "tyre_pressure_fr",
            "tyre_pressure_rl", "tyre_pressure_rr",
            "motor_temperature", "coolant_temperature",
            "throttle_position", "brake_position",
            "gear_position", "steering_angle"
        ],
        signal_defaults={
            "vehicle_speed": 60.0, "battery_soc": 80.0, "ev_range": 320.0,
            "tyre_pressure_fl": 220.0, "tyre_pressure_fr": 220.0,
            "tyre_pressure_rl": 220.0, "tyre_pressure_rr": 220.0,
            "motor_temperature": 45.0, "coolant_temperature": 40.0,
            "throttle_position": 30.0, "brake_position": 0.0,
            "gear_position": 3, "steering_angle": 0.0
        },
        thresholds={
            "battery_soc": {"warning": 20.0, "critical": 10.0},
            "motor_temperature": {"warning": 100.0, "critical": 115.0},
            "coolant_temperature": {"warning": 95.0, "critical": 105.0},
            "tyre_pressure": {"warning": 180.0, "critical": 150.0}
        },
        features=["Regenerative Braking", "Battery Health Monitor", "Range Prediction", "Motor Diagnostics"]
    ),
    
    "hybrid": VehicleVariant(
        name="Hybrid Electric Vehicle",
        variant_type="Hybrid",
        description="Combined ICE + electric motor with automatic mode switching",
        available_signals=[
            "vehicle_speed", "battery_soc", "ev_range",
            "tyre_pressure_fl", "tyre_pressure_fr",
            "tyre_pressure_rl", "tyre_pressure_rr",
            "motor_temperature", "coolant_temperature",
            "throttle_position", "brake_position",
            "gear_position", "steering_angle",
            "engine_rpm", "fuel_level"
        ],
        signal_defaults={
            "vehicle_speed": 60.0, "battery_soc": 65.0, "ev_range": 80.0,
            "tyre_pressure_fl": 230.0, "tyre_pressure_fr": 230.0,
            "tyre_pressure_rl": 230.0, "tyre_pressure_rr": 230.0,
            "motor_temperature": 50.0, "coolant_temperature": 45.0,
            "throttle_position": 35.0, "brake_position": 0.0,
            "gear_position": 4, "steering_angle": 0.0,
            "engine_rpm": 2000.0, "fuel_level": 70.0
        },
        thresholds={
            "battery_soc": {"warning": 15.0, "critical": 5.0},
            "motor_temperature": {"warning": 100.0, "critical": 115.0},
            "coolant_temperature": {"warning": 95.0, "critical": 105.0},
            "tyre_pressure": {"warning": 180.0, "critical": 150.0},
            "fuel_level": {"warning": 15.0, "critical": 5.0},
            "engine_rpm": {"warning": 6000.0, "critical": 7000.0}
        },
        features=["Hybrid Mode Control", "Engine Health", "Fuel Efficiency", "Battery + Fuel Range"]
    ),
    
    "ice": VehicleVariant(
        name="Internal Combustion Engine",
        variant_type="ICE",
        description="Traditional ICE vehicle with full engine diagnostics",
        available_signals=[
            "vehicle_speed",
            "tyre_pressure_fl", "tyre_pressure_fr",
            "tyre_pressure_rl", "tyre_pressure_rr",
            "coolant_temperature",
            "throttle_position", "brake_position",
            "gear_position", "steering_angle",
            "engine_rpm", "fuel_level", "oil_temperature"
        ],
        signal_defaults={
            "vehicle_speed": 60.0,
            "tyre_pressure_fl": 230.0, "tyre_pressure_fr": 230.0,
            "tyre_pressure_rl": 230.0, "tyre_pressure_rr": 230.0,
            "coolant_temperature": 50.0,
            "throttle_position": 35.0, "brake_position": 0.0,
            "gear_position": 4, "steering_angle": 0.0,
            "engine_rpm": 2500.0, "fuel_level": 65.0,
            "oil_temperature": 90.0
        },
        thresholds={
            "coolant_temperature": {"warning": 95.0, "critical": 110.0},
            "tyre_pressure": {"warning": 180.0, "critical": 150.0},
            "engine_rpm": {"warning": 6000.0, "critical": 7000.0},
            "fuel_level": {"warning": 15.0, "critical": 5.0},
            "oil_temperature": {"warning": 120.0, "critical": 140.0}
        },
        features=["Engine Diagnostics", "Oil Health", "Fuel Consumption", "Transmission Monitor"]
    )
}


def get_variant(variant_type: str) -> VehicleVariant:
    """
    Get vehicle variant configuration by type.
    
    Args:
        variant_type: One of "ev", "hybrid", "ice"
        
    Returns:
        VehicleVariant configuration
        
    Raises:
        ValueError: If variant_type is not recognized
    """
    variant_type = variant_type.lower()
    if variant_type not in VEHICLE_VARIANTS:
        valid = ", ".join(VEHICLE_VARIANTS.keys())
        raise ValueError(f"Unknown variant '{variant_type}'. Valid variants: {valid}")
    return VEHICLE_VARIANTS[variant_type]


def get_variant_names() -> List[str]:
    """Get list of available variant names."""
    return list(VEHICLE_VARIANTS.keys())
