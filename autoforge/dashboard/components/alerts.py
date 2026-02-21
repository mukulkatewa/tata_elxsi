"""Alert display components for the AutoForge Live Vehicle Dashboard.

This module provides alert rendering functions for displaying vehicle health alerts
with severity-based styling using Streamlit.
"""

import streamlit as st
import pandas as pd
from typing import List
from autoforge.dashboard.simulation.vehicle_simulator import Alert


def render_alert_panel(alerts: List[Alert]) -> None:
    """Display active alerts with severity-based styling.
    
    Args:
        alerts: List of Alert objects to display
        
    Styling:
        - CRITICAL alerts: Displayed with st.error (red background)
        - WARNING alerts: Displayed with st.warning (yellow background)
        - SUCCESS/INFO: Displayed with st.success (green background)
        
    Format:
        [SEVERITY] Signal: value (threshold: X) - Message
    """
    if not alerts:
        st.success("✓ All systems normal - No active alerts")
        return
    
    for alert in alerts:
        # Format alert message
        alert_message = (
            f"[{alert.severity}] {alert.signal_name}: {alert.current_value:.2f} "
            f"(threshold: {alert.threshold_value:.2f}) - {alert.message}"
        )
        
        # Display with severity-based styling
        if alert.severity == "CRITICAL":
            st.error(alert_message)
        elif alert.severity == "WARNING":
            st.warning(alert_message)
        else:
            # Handle any other severity levels gracefully
            st.info(alert_message)


def render_alert_history_table(alerts: List[Alert]) -> None:
    """Display historical alerts as a DataFrame.
    
    Args:
        alerts: List of Alert objects to display in table format
        
    The table includes columns for:
        - Timestamp: When the alert was generated
        - Severity: Alert severity level (WARNING/CRITICAL)
        - Signal: Signal name that triggered the alert
        - Value: Current signal value
        - Threshold: Threshold value that was exceeded
        - Message: Descriptive alert message
    """
    if not alerts:
        st.info("No alert history available")
        return
    
    # Convert alerts to DataFrame
    alert_data = []
    for alert in alerts:
        alert_data.append({
            "Timestamp": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Severity": alert.severity,
            "Signal": alert.signal_name,
            "Value": f"{alert.current_value:.2f}",
            "Threshold": f"{alert.threshold_value:.2f}",
            "Message": alert.message
        })
    
    df = pd.DataFrame(alert_data)
    
    # Display as Streamlit dataframe
    st.dataframe(df, use_container_width=True, hide_index=True)
