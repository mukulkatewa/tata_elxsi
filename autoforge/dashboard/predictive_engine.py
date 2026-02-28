"""
Predictive Diagnostics Engine for AutoForge Dashboard.

Analyzes vehicle signal trends to predict potential failures before they occur.
Uses linear regression and rule-based anomaly detection on historical signal data.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Prediction:
    """A single predictive diagnostic result."""
    signal_name: str
    prediction_type: str  # "time_to_threshold", "anomaly", "trend_warning"
    severity: str  # "INFO", "WARNING", "CRITICAL"
    message: str
    confidence: float  # 0.0 to 1.0
    estimated_time: Optional[float] = None  # seconds until event
    current_value: float = 0.0
    predicted_value: float = 0.0
    threshold: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Signal threshold configurations for prediction
PREDICTION_THRESHOLDS = {
    "battery_soc": {
        "warning": 20.0,
        "critical": 10.0,
        "unit": "%",
        "direction": "down",  # Alert when value goes DOWN
        "label": "Battery SOC"
    },
    "tyre_pressure_fl": {
        "warning": 180.0,
        "critical": 150.0,
        "unit": "kPa",
        "direction": "down",
        "label": "Tyre FL Pressure"
    },
    "tyre_pressure_fr": {
        "warning": 180.0,
        "critical": 150.0,
        "unit": "kPa",
        "direction": "down",
        "label": "Tyre FR Pressure"
    },
    "tyre_pressure_rl": {
        "warning": 180.0,
        "critical": 150.0,
        "unit": "kPa",
        "direction": "down",
        "label": "Tyre RL Pressure"
    },
    "tyre_pressure_rr": {
        "warning": 180.0,
        "critical": 150.0,
        "unit": "kPa",
        "direction": "down",
        "label": "Tyre RR Pressure"
    },
    "motor_temperature": {
        "warning": 100.0,
        "critical": 115.0,
        "unit": "°C",
        "direction": "up",  # Alert when value goes UP
        "label": "Motor Temperature"
    },
    "coolant_temperature": {
        "warning": 95.0,
        "critical": 105.0,
        "unit": "°C",
        "direction": "up",
        "label": "Coolant Temperature"
    }
}


class PredictiveEngine:
    """
    Predicts vehicle component failures using trend analysis.
    
    Techniques:
    - Linear regression on signal history to predict time-to-threshold
    - Rate-of-change anomaly detection
    - Pattern matching for known failure signatures
    """
    
    def __init__(self, tick_interval: float = 0.5):
        """
        Initialize the predictive engine.
        
        Args:
            tick_interval: Time between data points in seconds
        """
        self.tick_interval = tick_interval
        self._anomaly_history: Dict[str, List[float]] = {}
    
    def analyze(self, history_df: pd.DataFrame) -> List[Prediction]:
        """
        Run all predictive analyses on the signal history.
        
        Args:
            history_df: DataFrame with signal columns and timestamp
            
        Returns:
            List of Prediction objects sorted by severity
        """
        if history_df.empty or len(history_df) < 5:
            return []
        
        predictions = []
        
        # Run time-to-threshold predictions for each monitored signal
        for signal_name, config in PREDICTION_THRESHOLDS.items():
            if signal_name not in history_df.columns:
                continue
            
            signal_data = history_df[signal_name].values
            
            # Time-to-threshold prediction
            ttp = self._predict_time_to_threshold(signal_data, config)
            if ttp:
                predictions.append(ttp)
            
            # Anomaly detection
            anomaly = self._detect_anomaly(signal_name, signal_data, config)
            if anomaly:
                predictions.append(anomaly)
        
        # Driving pattern analysis
        driving_tips = self._analyze_driving_pattern(history_df)
        predictions.extend(driving_tips)
        
        # Sort by severity (CRITICAL > WARNING > INFO)
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        predictions.sort(key=lambda p: severity_order.get(p.severity, 3))
        
        return predictions
    
    def _predict_time_to_threshold(self, signal_data: np.ndarray, 
                                    config: Dict) -> Optional[Prediction]:
        """
        Use linear regression to predict when a signal will cross a threshold.
        
        Args:
            signal_data: Array of recent signal values
            config: Threshold configuration for this signal
            
        Returns:
            Prediction object if threshold crossing is predicted, None otherwise
        """
        if len(signal_data) < 5:
            return None
        
        # Use last 30 data points for trend
        recent = signal_data[-min(30, len(signal_data)):]
        x = np.arange(len(recent))
        
        # Linear regression
        try:
            slope, intercept = np.polyfit(x, recent, 1)
        except (np.linalg.LinAlgError, ValueError):
            return None
        
        current_value = recent[-1]
        direction = config["direction"]
        
        # Determine which threshold to check
        if direction == "down":
            # Signal decreasing toward threshold
            if slope >= 0:
                return None  # Not decreasing
            
            warning_threshold = config["warning"]
            critical_threshold = config["critical"]
            
            if current_value <= critical_threshold:
                return None  # Already past critical (handled by alerts)
            
            # Calculate ticks until threshold
            threshold = warning_threshold if current_value > warning_threshold else critical_threshold
            ticks_to_threshold = (threshold - current_value) / slope
            
        else:
            # Signal increasing toward threshold
            if slope <= 0:
                return None  # Not increasing
            
            warning_threshold = config["warning"]
            critical_threshold = config["critical"]
            
            if current_value >= critical_threshold:
                return None  # Already past critical
            
            threshold = warning_threshold if current_value < warning_threshold else critical_threshold
            ticks_to_threshold = (threshold - current_value) / slope
        
        if ticks_to_threshold < 0 or ticks_to_threshold > 300:
            return None  # Too far in the future or negative
        
        # Convert ticks to seconds
        time_seconds = ticks_to_threshold * self.tick_interval
        
        # Calculate confidence based on R² of fit
        predicted = slope * x + intercept
        ss_res = np.sum((recent - predicted) ** 2)
        ss_tot = np.sum((recent - np.mean(recent)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        confidence = max(0.0, min(1.0, r_squared))
        
        # Determine severity
        severity = "WARNING"
        if threshold == config.get("critical"):
            severity = "CRITICAL"
        if time_seconds < 10:
            severity = "CRITICAL"
        
        # Predicted value at threshold
        predicted_value = slope * (len(recent) + ticks_to_threshold) + intercept
        
        # Format time
        if time_seconds < 60:
            time_str = f"{time_seconds:.0f} seconds"
        else:
            time_str = f"{time_seconds / 60:.1f} minutes"
        
        return Prediction(
            signal_name=config["label"],
            prediction_type="time_to_threshold",
            severity=severity,
            message=f"{config['label']} predicted to reach {threshold}{config['unit']} in ~{time_str}",
            confidence=confidence,
            estimated_time=time_seconds,
            current_value=current_value,
            predicted_value=predicted_value,
            threshold=threshold
        )
    
    def _detect_anomaly(self, signal_name: str, signal_data: np.ndarray,
                        config: Dict) -> Optional[Prediction]:
        """
        Detect anomalous rate of change in a signal.
        
        Uses rolling standard deviation to identify sudden changes.
        """
        if len(signal_data) < 10:
            return None
        
        recent = signal_data[-min(20, len(signal_data)):]
        
        # Calculate rate of change
        diffs = np.diff(recent)
        
        if len(diffs) < 5:
            return None
        
        # Check for abnormal rate of change (> 3 standard deviations)
        mean_diff = np.mean(diffs)
        std_diff = np.std(diffs)
        
        if std_diff < 0.001:
            return None  # No variation
        
        latest_diff = diffs[-1]
        z_score = abs((latest_diff - mean_diff) / std_diff)
        
        if z_score < 3.0:
            return None
        
        # Store for pattern tracking
        if signal_name not in self._anomaly_history:
            self._anomaly_history[signal_name] = []
        self._anomaly_history[signal_name].append(z_score)
        
        # Only alert if multiple anomalies detected
        if len(self._anomaly_history[signal_name]) < 2:
            return None
        
        return Prediction(
            signal_name=config["label"],
            prediction_type="anomaly",
            severity="WARNING",
            message=f"{config['label']} showing abnormal variation pattern (z-score: {z_score:.1f})",
            confidence=min(1.0, z_score / 5.0),
            current_value=recent[-1],
            predicted_value=recent[-1] + latest_diff,
            threshold=config["warning"]
        )
    
    def _analyze_driving_pattern(self, history_df: pd.DataFrame) -> List[Prediction]:
        """
        Analyze driving pattern and provide recommendations.
        """
        tips = []
        
        if "vehicle_speed" not in history_df.columns:
            return tips
        
        speed = history_df["vehicle_speed"].values
        
        if len(speed) < 10:
            return tips
        
        recent_speed = speed[-20:]
        
        # Detect hard braking (large negative speed changes)
        speed_diffs = np.diff(recent_speed)
        hard_brakes = np.sum(speed_diffs < -10)
        
        if hard_brakes >= 3:
            tips.append(Prediction(
                signal_name="Driving Pattern",
                prediction_type="trend_warning",
                severity="INFO",
                message=f"Frequent hard braking detected ({hard_brakes} instances). Smoother braking improves tyre life and range.",
                confidence=0.8,
                current_value=hard_brakes
            ))
        
        # Detect rapid acceleration
        hard_accels = np.sum(speed_diffs > 15)
        if hard_accels >= 3:
            tips.append(Prediction(
                signal_name="Driving Pattern",
                prediction_type="trend_warning",
                severity="INFO",
                message=f"Rapid acceleration detected ({hard_accels} instances). Gentle acceleration improves battery range by up to 15%.",
                confidence=0.7,
                current_value=hard_accels
            ))
        
        # Speed consistency analysis
        speed_std = np.std(recent_speed)
        if speed_std > 25 and np.mean(recent_speed) > 60:
            tips.append(Prediction(
                signal_name="Driving Pattern",
                prediction_type="trend_warning",
                severity="INFO",
                message="Speed variation is high. Maintaining steady speed improves range and reduces wear.",
                confidence=0.6,
                current_value=speed_std
            ))
        
        return tips
