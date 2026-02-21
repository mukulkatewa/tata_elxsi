"""
Vehicle Signal Simulator for AutoForge Live Dashboard.

This module provides the VehicleSimulator class that maintains and updates
simulated Vehicle Signal Specification (VSS) compliant signals.
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Alert:
    """Alert data model for threshold violations."""
    signal_name: str
    current_value: float
    threshold_value: float
    severity: str  # "WARNING" or "CRITICAL"
    message: str
    timestamp: datetime


class VehicleSimulator:
    """
    Simulates realistic vehicle signals compliant with VSS specification.
    
    Maintains state for 13 VSS signals and supports fault scenario injection.
    """
    
    def __init__(self, scenario: str = "normal"):
        """
        Initialize simulator with realistic starting values.
        
        Args:
            scenario: Initial scenario mode (default: "normal")
        """
        # VSS Signal state variables - initialized with realistic defaults
        self.vehicle_speed: float = 60.0  # kmh
        
        # Tyre pressures (all four tyres)
        self.tyre_pressure_fl: float = 220.0  # kPa (front-left)
        self.tyre_pressure_fr: float = 220.0  # kPa (front-right)
        self.tyre_pressure_rl: float = 220.0  # kPa (rear-left)
        self.tyre_pressure_rr: float = 220.0  # kPa (rear-right)
        
        # Battery and range
        self.battery_soc: float = 85.0  # %
        self.ev_range: float = 425.0  # km (85% * 5.0)
        
        # Control positions
        self.throttle_position: float = 30.0  # %
        self.brake_position: float = 0.0  # %
        self.gear_position: int = 4  # 0-8
        self.steering_angle: float = 0.0  # degrees
        
        # Temperatures
        self.motor_temperature: float = 80.0  # C
        self.coolant_temperature: float = 75.0  # C
        
        # Internal state tracking
        self._scenario_state: Dict = {"name": scenario, "active": False}
        self._tick_count: int = 0
