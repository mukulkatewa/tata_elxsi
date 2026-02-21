"""Gauge visualization components for the AutoForge Live Vehicle Dashboard.

This module provides gauge rendering functions for displaying real-time vehicle signals
using Plotly with a consistent dark theme.
"""

import plotly.graph_objects as go
import streamlit as st


# Dark theme configuration for all gauges
GAUGE_THEME = {
    "paper_bgcolor": "#0d1117",
    "plot_bgcolor": "#0d1117",
    "font": {"color": "white"},
    "height": 200
}

# Speedometer color ranges (0-200 kmh)
# Green: 0-80 kmh (safe city speeds)
# Yellow: 80-130 kmh (highway speeds)
# Red: 130-200 kmh (high speeds)
SPEEDOMETER_RANGES = [
    {"range": [0, 80], "color": "green"},
    {"range": [80, 130], "color": "yellow"},
    {"range": [130, 200], "color": "red"}
]

# Tyre pressure color ranges (150-350 kPa)
# Red: 150-180 kPa (low pressure - warning/critical)
# Green: 180-280 kPa (normal operating range)
# Yellow: 280-350 kPa (high pressure)
TYRE_PRESSURE_RANGES = [
    {"range": [150, 180], "color": "red"},
    {"range": [180, 280], "color": "green"},
    {"range": [280, 350], "color": "yellow"}
]

# Battery SOC color ranges (0-100%)
# Red: 0-20% (low battery - warning/critical)
# Yellow: 20-40% (moderate battery)
# Green: 40-100% (good battery level)
BATTERY_RANGES = [
    {"range": [0, 20], "color": "red"},
    {"range": [20, 40], "color": "yellow"},
    {"range": [40, 100], "color": "green"}
]

# Temperature color ranges (20-120 C)
# Green: 20-100 C (normal operating temperature)
# Yellow: 100-115 C (elevated temperature - warning)
# Red: 115-120 C (critical temperature)
TEMPERATURE_RANGES = [
    {"range": [20, 100], "color": "green"},
    {"range": [100, 115], "color": "yellow"},
    {"range": [115, 120], "color": "red"}
]


def render_speedometer(speed: float) -> None:
    """Display vehicle speed gauge (0-200 kmh).
    
    Args:
        speed: Current vehicle speed in kmh (0-200)
        
    Color zones:
        - Green: 0-80 kmh (safe city speeds)
        - Yellow: 80-130 kmh (highway speeds)
        - Red: 130-200 kmh (high speeds)
    """
    # Clamp speed to valid range
    speed = max(0, min(200, speed))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=speed,
        title={"text": "Speed (kmh)", "font": {"color": "white"}},
        number={"font": {"color": "white"}},
        gauge={
            "axis": {"range": [0, 200], "tickcolor": "white"},
            "bar": {"color": "white"},
            "steps": SPEEDOMETER_RANGES,
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": speed
            }
        }
    ))
    
    fig.update_layout(**GAUGE_THEME)
    st.plotly_chart(fig, use_container_width=True)


def render_tyre_pressure_gauge(pressure: float, position: str) -> None:
    """Display tyre pressure gauge (150-350 kPa).
    
    Args:
        pressure: Current tyre pressure in kPa (150-350)
        position: Tyre position label (e.g., "FL", "FR", "RL", "RR")
        
    Color zones:
        - Red: 150-180 kPa (low pressure - warning/critical)
        - Green: 180-280 kPa (normal operating range)
        - Yellow: 280-350 kPa (high pressure)
    """
    # Clamp pressure to valid range
    pressure = max(150, min(350, pressure))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pressure,
        title={"text": f"Tyre {position} (kPa)", "font": {"color": "white"}},
        number={"font": {"color": "white"}},
        gauge={
            "axis": {"range": [150, 350], "tickcolor": "white"},
            "bar": {"color": "white"},
            "steps": TYRE_PRESSURE_RANGES,
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": pressure
            }
        }
    ))
    
    fig.update_layout(**GAUGE_THEME)
    st.plotly_chart(fig, use_container_width=True)


def render_battery_gauge(soc: float) -> None:
    """Display battery state of charge as horizontal bar (0-100%).
    
    Args:
        soc: Battery state of charge percentage (0-100)
        
    Color zones:
        - Red: 0-20% (low battery - warning/critical)
        - Yellow: 20-40% (moderate battery)
        - Green: 40-100% (good battery level)
    """
    # Clamp SOC to valid range
    soc = max(0, min(100, soc))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soc,
        title={"text": "Battery SOC (%)", "font": {"color": "white"}},
        number={"font": {"color": "white"}, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white"},
            "bar": {"color": "white"},
            "steps": BATTERY_RANGES,
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": soc
            },
            "shape": "bullet"  # Horizontal bar style
        }
    ))
    
    fig.update_layout(**GAUGE_THEME)
    st.plotly_chart(fig, use_container_width=True)


def render_temperature_gauge(temp: float, label: str) -> None:
    """Display temperature gauge in thermometer style (20-120 C).
    
    Args:
        temp: Current temperature in Celsius (20-120)
        label: Temperature label (e.g., "Motor", "Coolant")
        
    Color zones:
        - Green: 20-100 C (normal operating temperature)
        - Yellow: 100-115 C (elevated temperature - warning)
        - Red: 115-120 C (critical temperature)
    """
    # Clamp temperature to valid range
    temp = max(20, min(120, temp))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=temp,
        title={"text": f"{label} Temp (°C)", "font": {"color": "white"}},
        number={"font": {"color": "white"}, "suffix": "°C"},
        gauge={
            "axis": {"range": [20, 120], "tickcolor": "white"},
            "bar": {"color": "white"},
            "steps": TEMPERATURE_RANGES,
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": temp
            }
        }
    ))
    
    fig.update_layout(**GAUGE_THEME)
    st.plotly_chart(fig, use_container_width=True)
