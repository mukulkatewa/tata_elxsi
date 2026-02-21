"""
Vehicle Signal Simulator for AutoForge Live Dashboard.

This module provides the VehicleSimulator class that maintains and updates
simulated Vehicle Signal Specification (VSS) compliant signals.
"""

import numpy as np
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

    def tick(self) -> Dict[str, float]:
        """
        Update all signals and return current state as VSS-style dictionary.
        
        In normal mode, applies random walk updates with signal-specific deltas:
        - vehicle_speed: ±5 kmh
        - tyre_pressure: ±1 kPa
        - battery_soc: -0.05% (drain)
        
        Updates ev_range based on battery_soc and gear_position.
        
        Returns:
            Dictionary with VSS-style keys and current signal values
        """
        # Increment tick count
        self._tick_count += 1
        
        # Apply random walk updates in normal mode
        if not self._scenario_state.get("active", False):
            # Vehicle speed: ±5 kmh
            self.vehicle_speed += np.random.uniform(-5.0, 5.0)
            self.vehicle_speed = np.clip(self.vehicle_speed, 0.0, 200.0)
            
            # Tyre pressures: ±1 kPa for each tyre
            self.tyre_pressure_fl += np.random.uniform(-1.0, 1.0)
            self.tyre_pressure_fl = np.clip(self.tyre_pressure_fl, 150.0, 350.0)
            
            self.tyre_pressure_fr += np.random.uniform(-1.0, 1.0)
            self.tyre_pressure_fr = np.clip(self.tyre_pressure_fr, 150.0, 350.0)
            
            self.tyre_pressure_rl += np.random.uniform(-1.0, 1.0)
            self.tyre_pressure_rl = np.clip(self.tyre_pressure_rl, 150.0, 350.0)
            
            self.tyre_pressure_rr += np.random.uniform(-1.0, 1.0)
            self.tyre_pressure_rr = np.clip(self.tyre_pressure_rr, 150.0, 350.0)
            
            # Battery SOC: -0.05% drain per tick
            self.battery_soc -= 0.05
            self.battery_soc = np.clip(self.battery_soc, 0.0, 100.0)
            
            # Throttle and brake: small random variations
            self.throttle_position += np.random.uniform(-2.0, 2.0)
            self.throttle_position = np.clip(self.throttle_position, 0.0, 100.0)
            
            self.brake_position += np.random.uniform(-1.0, 1.0)
            self.brake_position = np.clip(self.brake_position, 0.0, 100.0)
            
            # Steering angle: small variations
            self.steering_angle += np.random.uniform(-10.0, 10.0)
            self.steering_angle = np.clip(self.steering_angle, -540.0, 540.0)
            
            # Temperatures: small variations
            self.motor_temperature += np.random.uniform(-0.5, 0.5)
            self.motor_temperature = np.clip(self.motor_temperature, 20.0, 120.0)
            
            self.coolant_temperature += np.random.uniform(-0.5, 0.5)
            self.coolant_temperature = np.clip(self.coolant_temperature, 20.0, 110.0)
        
        # Update ev_range based on battery_soc and gear_position
        # Base formula: ev_range = battery_soc * 5.0
        # Gear adjustment: higher gears are more efficient
        base_range = self.battery_soc * 5.0
        
        # Gear efficiency factor (higher gears = better efficiency)
        # Gear 0 (neutral/park): 0.5x, Gear 1-2: 0.7x, Gear 3-4: 1.0x, Gear 5+: 1.1x
        if self.gear_position == 0:
            gear_factor = 0.5
        elif self.gear_position <= 2:
            gear_factor = 0.7
        elif self.gear_position <= 4:
            gear_factor = 1.0
        else:
            gear_factor = 1.1
        
        # Speed adjustment: higher speeds reduce efficiency
        if self.vehicle_speed > 100:
            speed_factor = 0.9
        elif self.vehicle_speed > 130:
            speed_factor = 0.8
        else:
            speed_factor = 1.0
        
        self.ev_range = base_range * gear_factor * speed_factor
        self.ev_range = np.clip(self.ev_range, 0.0, 500.0)
        
        # Return complete signal dictionary with VSS-style keys
        return {
            "vehicle_speed": float(self.vehicle_speed),
            "tyre_pressure_fl": float(self.tyre_pressure_fl),
            "tyre_pressure_fr": float(self.tyre_pressure_fr),
            "tyre_pressure_rl": float(self.tyre_pressure_rl),
            "tyre_pressure_rr": float(self.tyre_pressure_rr),
            "battery_soc": float(self.battery_soc),
            "ev_range": float(self.ev_range),
            "throttle_position": float(self.throttle_position),
            "brake_position": float(self.brake_position),
            "gear_position": int(self.gear_position),
            "steering_angle": float(self.steering_angle),
            "motor_temperature": float(self.motor_temperature),
            "coolant_temperature": float(self.coolant_temperature),
        }

    def get_alert_status(self) -> List[Alert]:
        """
        Evaluate thresholds and return list of active alerts.
        
        Checks all monitored signals against defined thresholds:
        - Tyre pressure: WARNING < 180 kPa, CRITICAL < 150 kPa
        - Battery SOC: WARNING < 20%, CRITICAL < 10%
        - Motor temperature: WARNING > 100 C, CRITICAL > 115 C
        - Coolant temperature: WARNING > 95 C, CRITICAL > 105 C
        
        Returns:
            List of Alert objects for all active threshold violations
        """
        alerts = []
        timestamp = datetime.now()
        
        # Check tyre pressures (all four tyres)
        tyre_pressures = [
            ("tyre_pressure_fl", self.tyre_pressure_fl, "Front Left"),
            ("tyre_pressure_fr", self.tyre_pressure_fr, "Front Right"),
            ("tyre_pressure_rl", self.tyre_pressure_rl, "Rear Left"),
            ("tyre_pressure_rr", self.tyre_pressure_rr, "Rear Right"),
        ]
        
        for signal_name, pressure, position in tyre_pressures:
            if pressure < 150.0:
                alerts.append(Alert(
                    signal_name=signal_name,
                    current_value=pressure,
                    threshold_value=150.0,
                    severity="CRITICAL",
                    message=f"{position} tyre pressure critically low: {pressure:.1f} kPa (threshold: 150 kPa)",
                    timestamp=timestamp
                ))
            elif pressure < 180.0:
                alerts.append(Alert(
                    signal_name=signal_name,
                    current_value=pressure,
                    threshold_value=180.0,
                    severity="WARNING",
                    message=f"{position} tyre pressure low: {pressure:.1f} kPa (threshold: 180 kPa)",
                    timestamp=timestamp
                ))
        
        # Check battery SOC
        if self.battery_soc < 10.0:
            alerts.append(Alert(
                signal_name="battery_soc",
                current_value=self.battery_soc,
                threshold_value=10.0,
                severity="CRITICAL",
                message=f"Battery critically low: {self.battery_soc:.1f}% (threshold: 10%)",
                timestamp=timestamp
            ))
        elif self.battery_soc < 20.0:
            alerts.append(Alert(
                signal_name="battery_soc",
                current_value=self.battery_soc,
                threshold_value=20.0,
                severity="WARNING",
                message=f"Battery low: {self.battery_soc:.1f}% (threshold: 20%)",
                timestamp=timestamp
            ))
        
        # Check motor temperature
        if self.motor_temperature > 115.0:
            alerts.append(Alert(
                signal_name="motor_temperature",
                current_value=self.motor_temperature,
                threshold_value=115.0,
                severity="CRITICAL",
                message=f"Motor critically overheating: {self.motor_temperature:.1f}°C (threshold: 115°C)",
                timestamp=timestamp
            ))
        elif self.motor_temperature > 100.0:
            alerts.append(Alert(
                signal_name="motor_temperature",
                current_value=self.motor_temperature,
                threshold_value=100.0,
                severity="WARNING",
                message=f"Motor temperature high: {self.motor_temperature:.1f}°C (threshold: 100°C)",
                timestamp=timestamp
            ))
        
        # Check coolant temperature
        if self.coolant_temperature > 105.0:
            alerts.append(Alert(
                signal_name="coolant_temperature",
                current_value=self.coolant_temperature,
                threshold_value=105.0,
                severity="CRITICAL",
                message=f"Coolant critically overheating: {self.coolant_temperature:.1f}°C (threshold: 105°C)",
                timestamp=timestamp
            ))
        elif self.coolant_temperature > 95.0:
            alerts.append(Alert(
                signal_name="coolant_temperature",
                current_value=self.coolant_temperature,
                threshold_value=95.0,
                severity="WARNING",
                message=f"Coolant temperature high: {self.coolant_temperature:.1f}°C (threshold: 95°C)",
                timestamp=timestamp
            ))
        
        return alerts
