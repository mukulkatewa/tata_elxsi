"""
AutoForge Live Vehicle Dashboard

Main Streamlit application for real-time vehicle health monitoring.
Displays simulated VSS signals, fault scenarios, and alerts through an interactive web interface.
"""

import time
import os
import streamlit as st
from autoforge.dashboard import data_bridge
from autoforge.dashboard.components.gauges import (
    render_speedometer,
    render_tyre_pressure_gauge,
    render_battery_gauge,
    render_temperature_gauge
)
from autoforge.dashboard.components.charts import (
    render_tyre_pressure_trend,
    render_battery_trend,
    render_speed_trend,
    render_temperature_trend
)
from autoforge.dashboard.components.alerts import (
    render_alert_panel,
    render_alert_history_table
)
from autoforge.dashboard.simulation.scenarios import SCENARIOS


# Page configuration
st.set_page_config(
    page_title="AutoForge — Vehicle Health",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS injection
DARK_THEME_CSS = """
<style>
    /* Main background */
    .stApp {
        background-color: #0d1117;
        color: white;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Text */
    p, span, div {
        color: white;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #238636;
        color: white;
        border: none;
        border-radius: 6px;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #0d1117;
        color: white;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: #238636;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: #0d1117;
    }
</style>
"""

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)


def render_header():
    """Render dashboard header with logo and live status indicator."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🚗 AutoForge — Vehicle Health")
    
    with col2:
        st.markdown("### 🟢 LIVE")


def render_scenario_controls():
    """Render sidebar scenario controls (selector, apply, reset, tick speed)."""
    st.sidebar.header("Scenario Controls")
    
    # Scenario selector dropdown
    scenario_names = list(SCENARIOS.keys())
    selected_scenario = st.sidebar.selectbox(
        "Select Scenario",
        options=scenario_names,
        index=0,
        key="selected_scenario"
    )
    
    # Display scenario description
    if selected_scenario in SCENARIOS:
        st.sidebar.info(SCENARIOS[selected_scenario].description)
    
    # Apply and Reset buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("Apply", width='stretch'):
            data_bridge.apply_scenario(selected_scenario)
            st.success(f"Applied: {selected_scenario}")
    
    with col2:
        if st.button("Reset", width='stretch'):
            data_bridge.reset_simulator()
            st.success("Reset to normal mode")
    
    # Tick speed slider
    st.sidebar.markdown("---")
    tick_speed = st.sidebar.slider(
        "Tick Speed (seconds)",
        min_value=0.1,
        max_value=2.0,
        value=0.5,
        step=0.1,
        key="tick_speed"
    )
    
    st.sidebar.caption(f"Refresh interval: {tick_speed}s")


def render_generated_services_list():
    """Check outputs folder and display generated services or 'No generated services available'."""
    st.sidebar.markdown("---")
    st.sidebar.header("Generated Services")
    
    outputs_path = "outputs"
    
    # Check if outputs folder exists
    if not os.path.exists(outputs_path):
        st.sidebar.info("No generated services available")
        return
    
    # List contents of outputs folder
    try:
        services = os.listdir(outputs_path)
        
        if not services:
            st.sidebar.info("No generated services available")
        else:
            st.sidebar.success(f"Found {len(services)} service(s)")
            for service in services:
                st.sidebar.text(f"• {service}")
    except Exception as e:
        st.sidebar.error(f"Error reading outputs: {e}")


def render_generated_code_viewer():
    """Display generated code from outputs folder."""
    outputs_path = "outputs"
    
    if not os.path.exists(outputs_path):
        st.info("No generated code available. Run the code generation pipeline to create services.")
        return
    
    try:
        services = os.listdir(outputs_path)
        
        if not services:
            st.info("No generated code available. Run the code generation pipeline to create services.")
        else:
            # Let user select a service to view
            selected_service = st.selectbox("Select Service", options=services)
            
            if selected_service:
                service_path = os.path.join(outputs_path, selected_service)
                
                # List files in the service directory
                if os.path.isdir(service_path):
                    files = [f for f in os.listdir(service_path) if os.path.isfile(os.path.join(service_path, f))]
                    
                    if files:
                        selected_file = st.selectbox("Select File", options=files)
                        
                        if selected_file:
                            file_path = os.path.join(service_path, selected_file)
                            
                            try:
                                with open(file_path, 'r') as f:
                                    code_content = f.read()
                                
                                st.code(code_content, language="python")
                            except Exception as e:
                                st.error(f"Error reading file: {e}")
                    else:
                        st.info("No files found in this service directory")
                else:
                    st.info("Selected item is not a directory")
    except Exception as e:
        st.error(f"Error accessing outputs folder: {e}")


# Header
render_header()

# Sidebar
render_scenario_controls()
render_generated_services_list()

# Initialize simulator on first run
if "simulator" not in st.session_state:
    data_bridge.initialize_simulator()

# Main content - continuous refresh loop
current_state = data_bridge.get_next_tick()
alerts = data_bridge.get_current_alerts()
history_df = data_bridge.get_history()

# Alerts row at top
st.markdown("## 🚨 Active Alerts")
render_alert_panel(alerts)

st.markdown("---")

# Gauges row with 6 columns
st.markdown("## 📊 Real-Time Gauges")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    render_speedometer(current_state["vehicle_speed"])

with col2:
    render_tyre_pressure_gauge(current_state["tyre_pressure_fl"], "FL")

with col3:
    render_tyre_pressure_gauge(current_state["tyre_pressure_fr"], "FR")

with col4:
    render_tyre_pressure_gauge(current_state["tyre_pressure_rl"], "RL")

with col5:
    render_tyre_pressure_gauge(current_state["tyre_pressure_rr"], "RR")

with col6:
    render_battery_gauge(current_state["battery_soc"])

st.markdown("---")

# Chart rows
st.markdown("## 📈 Trend Charts")

# First chart row: Tyre Pressure and Battery
col1, col2 = st.columns(2)

with col1:
    render_tyre_pressure_trend(history_df)

with col2:
    render_battery_trend(history_df)

# Second chart row: Speed and Temperature
col1, col2 = st.columns(2)

with col1:
    render_speed_trend(history_df)

with col2:
    render_temperature_trend(history_df)

st.markdown("---")

# Bottom tabs for Raw Signals, Alert Log, Generated Code
st.markdown("## 📋 Detailed Views")
tab1, tab2, tab3 = st.tabs(["Raw Signals", "Alert Log", "Generated Code"])

with tab1:
    st.subheader("Raw Signal Data")
    if not history_df.empty:
        # Display most recent signals at the top
        display_df = history_df.tail(20).sort_values("timestamp", ascending=False)
        st.dataframe(display_df, width='stretch', hide_index=True)
    else:
        st.info("No signal data available yet")

with tab2:
    st.subheader("Alert History")
    render_alert_history_table(alerts)

with tab3:
    st.subheader("Generated Code Viewer")
    render_generated_code_viewer()

# Sleep based on tick speed slider and rerun for continuous updates
time.sleep(st.session_state.get("tick_speed", 0.5))
st.rerun()
