"""Chart visualization components for the AutoForge Live Vehicle Dashboard.

This module provides trend chart rendering functions for displaying time-series vehicle signals
using Plotly with a consistent dark theme.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# Dark theme configuration for all charts
CHART_THEME = {
    "paper_bgcolor": "#0d1117",
    "plot_bgcolor": "#0d1117",
    "font": {"color": "white"},
    "height": 300,
    "xaxis": {"gridcolor": "#21262d", "color": "white"},
    "yaxis": {"gridcolor": "#21262d", "color": "white"}
}

# Threshold line styling for warning lines
THRESHOLD_LINE_STYLE = {
    "color": "red",
    "width": 2,
    "dash": "dash"
}


def render_tyre_pressure_trend(history_df: pd.DataFrame) -> None:
    """Display tyre pressure trend chart with 4 line traces and 180 kPa threshold line.
    
    Args:
        history_df: DataFrame with timestamp and tyre pressure columns (last 60 ticks)
        
    Features:
        - 4 line traces for FL, FR, RL, RR tyre pressures
        - Red dashed threshold line at 180 kPa (WARNING level)
        - 60-tick rolling window
        - 300px height
        - Dark theme styling
    """
    if history_df.empty:
        st.info("No tyre pressure data available yet")
        return
    
    # Take last 60 data points
    df = history_df.tail(60)
    
    fig = go.Figure()
    
    # Add line traces for each tyre
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["tyre_pressure_fl"],
        mode="lines",
        name="Front Left",
        line={"color": "#58a6ff", "width": 2}
    ))
    
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["tyre_pressure_fr"],
        mode="lines",
        name="Front Right",
        line={"color": "#79c0ff", "width": 2}
    ))
    
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["tyre_pressure_rl"],
        mode="lines",
        name="Rear Left",
        line={"color": "#a5d6ff", "width": 2}
    ))
    
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["tyre_pressure_rr"],
        mode="lines",
        name="Rear Right",
        line={"color": "#c9e6ff", "width": 2}
    ))
    
    # Add threshold line at 180 kPa
    fig.add_hline(
        y=180,
        line=THRESHOLD_LINE_STYLE,
        annotation_text="WARNING (180 kPa)",
        annotation_position="right"
    )
    
    fig.update_layout(
        **CHART_THEME,
        title={"text": "Tyre Pressure Trend", "font": {"color": "white"}},
        xaxis_title="Time",
        yaxis_title="Pressure (kPa)",
        legend={"font": {"color": "white"}}
    )
    
    st.plotly_chart(fig, width='stretch')


def render_battery_trend(history_df: pd.DataFrame) -> None:
    """Display battery trend as area chart with dual Y-axes (soc % and range km).
    
    Args:
        history_df: DataFrame with timestamp, battery_soc, and ev_range columns (last 60 ticks)
        
    Features:
        - Area chart for battery SOC (left Y-axis, %)
        - Area chart for EV range (right Y-axis, km)
        - 60-tick rolling window
        - 300px height
        - Dark theme styling
    """
    if history_df.empty:
        st.info("No battery data available yet")
        return
    
    # Take last 60 data points
    df = history_df.tail(60)
    
    fig = go.Figure()
    
    # Add battery SOC area chart (left Y-axis)
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["battery_soc"],
        mode="lines",
        name="Battery SOC",
        fill="tozeroy",
        line={"color": "#56d364", "width": 2},
        yaxis="y"
    ))
    
    # Add EV range area chart (right Y-axis)
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["ev_range"],
        mode="lines",
        name="EV Range",
        fill="tozeroy",
        line={"color": "#f778ba", "width": 2},
        yaxis="y2"
    ))
    
    # Create a modified theme for battery_trend that excludes yaxis
    battery_theme = {k: v for k, v in CHART_THEME.items() if k != "yaxis"}
    
    fig.update_layout(
        **battery_theme,
        title={"text": "Battery & Range Trend", "font": {"color": "white"}},
        xaxis_title="Time",
        yaxis=dict(
            title="Battery SOC (%)",
            gridcolor="#21262d",
            color="white"
        ),
        yaxis2=dict(
            title="EV Range (km)",
            overlaying="y",
            side="right",
            gridcolor="#21262d",
            color="white"
        ),
        legend={"font": {"color": "white"}}
    )
    
    st.plotly_chart(fig, width='stretch')


def render_speed_trend(history_df: pd.DataFrame) -> None:
    """Display vehicle speed trend as line chart.
    
    Args:
        history_df: DataFrame with timestamp and vehicle_speed columns (last 60 ticks)
        
    Features:
        - Single line trace for vehicle speed
        - 60-tick rolling window
        - 300px height
        - Dark theme styling
    """
    if history_df.empty:
        st.info("No speed data available yet")
        return
    
    # Take last 60 data points
    df = history_df.tail(60)
    
    fig = go.Figure()
    
    # Add speed line trace
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["vehicle_speed"],
        mode="lines",
        name="Vehicle Speed",
        line={"color": "#58a6ff", "width": 2}
    ))
    
    fig.update_layout(
        **CHART_THEME,
        title={"text": "Vehicle Speed Trend", "font": {"color": "white"}},
        xaxis_title="Time",
        yaxis_title="Speed (kmh)",
        legend={"font": {"color": "white"}}
    )
    
    st.plotly_chart(fig, width='stretch')


def render_temperature_trend(history_df: pd.DataFrame) -> None:
    """Display temperature trend with 2 traces and warning threshold lines.
    
    Args:
        history_df: DataFrame with timestamp, motor_temperature, and coolant_temperature columns (last 60 ticks)
        
    Features:
        - 2 line traces for motor and coolant temperatures
        - Red dashed threshold lines at 100°C (motor WARNING) and 95°C (coolant WARNING)
        - 60-tick rolling window
        - 300px height
        - Dark theme styling
    """
    if history_df.empty:
        st.info("No temperature data available yet")
        return
    
    # Take last 60 data points
    df = history_df.tail(60)
    
    fig = go.Figure()
    
    # Add motor temperature trace
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["motor_temperature"],
        mode="lines",
        name="Motor Temp",
        line={"color": "#f85149", "width": 2}
    ))
    
    # Add coolant temperature trace
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["coolant_temperature"],
        mode="lines",
        name="Coolant Temp",
        line={"color": "#79c0ff", "width": 2}
    ))
    
    # Add threshold line at 100°C for motor
    fig.add_hline(
        y=100,
        line=THRESHOLD_LINE_STYLE,
        annotation_text="Motor WARNING (100°C)",
        annotation_position="right"
    )
    
    # Add threshold line at 95°C for coolant
    fig.add_hline(
        y=95,
        line={**THRESHOLD_LINE_STYLE, "dash": "dot"},
        annotation_text="Coolant WARNING (95°C)",
        annotation_position="left"
    )
    
    fig.update_layout(
        **CHART_THEME,
        title={"text": "Temperature Trend", "font": {"color": "white"}},
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        legend={"font": {"color": "white"}}
    )
    
    st.plotly_chart(fig, width='stretch')
