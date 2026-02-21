"""
Data Bridge Module

Manages state persistence and data flow between VehicleSimulator and Streamlit UI.
Uses Streamlit's session_state to persist simulator instance, history buffer, and metadata.
"""

from datetime import datetime
from typing import Dict, List
import pandas as pd
import streamlit as st

from autoforge.dashboard.simulation.vehicle_simulator import VehicleSimulator, Alert


def initialize_simulator(scenario: str = "normal") -> None:
    """
    Create or reset VehicleSimulator in session_state.
    
    Args:
        scenario: Initial scenario name (default: "normal")
    """
    st.session_state.simulator = VehicleSimulator(scenario=scenario)
    st.session_state.history = []
    st.session_state.tick_count = 0
    st.session_state.start_time = datetime.now()


def get_next_tick() -> Dict[str, float]:
    """
    Call simulator.tick(), append to history buffer, return current state.
    
    Returns:
        Dictionary of current signal values with VSS-style keys
    """
    # Ensure simulator is initialized
    if "simulator" not in st.session_state:
        initialize_simulator()
    
    # Get next tick from simulator
    current_state = st.session_state.simulator.tick()
    
    # Create history entry with timestamp
    history_entry = {
        "timestamp": datetime.now(),
        **current_state
    }
    
    # Append to history buffer
    st.session_state.history.append(history_entry)
    
    # Maintain FIFO buffer (max 60 entries)
    if len(st.session_state.history) > 60:
        st.session_state.history = st.session_state.history[-60:]
    
    # Increment tick count
    st.session_state.tick_count = st.session_state.get("tick_count", 0) + 1
    
    return current_state


def get_history() -> pd.DataFrame:
    """
    Return history buffer as DataFrame with timestamp column.
    
    Returns:
        pandas DataFrame with timestamp and all signal columns
    """
    # Ensure history exists
    if "history" not in st.session_state or not st.session_state.history:
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=[
            "timestamp", "vehicle_speed", "tyre_pressure_fl", "tyre_pressure_fr",
            "tyre_pressure_rl", "tyre_pressure_rr", "battery_soc", "ev_range",
            "throttle_position", "brake_position", "gear_position", "steering_angle",
            "motor_temperature", "coolant_temperature"
        ])
    
    # Convert history list to DataFrame
    df = pd.DataFrame(st.session_state.history)
    
    return df


def get_current_alerts() -> List[Alert]:
    """
    Return current alert list from simulator.
    
    Returns:
        List of Alert objects
    """
    # Ensure simulator is initialized
    if "simulator" not in st.session_state:
        initialize_simulator()
    
    return st.session_state.simulator.get_alert_status()


def apply_scenario(scenario_name: str) -> None:
    """
    Trigger scenario on simulator.
    
    Args:
        scenario_name: Name of the scenario to apply
    """
    # Ensure simulator is initialized
    if "simulator" not in st.session_state:
        initialize_simulator()
    
    st.session_state.simulator.trigger_scenario(scenario_name)


def reset_simulator() -> None:
    """
    Reinitialize simulator to normal mode.
    """
    initialize_simulator(scenario="normal")
