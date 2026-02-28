"""
AutoForge Live Vehicle Dashboard Page

Real-time vehicle health monitoring with VSS signal simulation,
predictive diagnostics, and fault scenario injection.
"""

import time
import os
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is on sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(Path(PROJECT_ROOT) / ".env")
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
from autoforge.dashboard.predictive_engine import PredictiveEngine
from autoforge.vehicle_variants import VEHICLE_VARIANTS, get_variant
from autoforge.ota_registry import OTAServiceRegistry


def render_live_dashboard():
    """Render the full live vehicle dashboard."""
    
    # Initialize session state
    if "predictive_engine" not in st.session_state:
        st.session_state.predictive_engine = PredictiveEngine()
    if "ota_registry" not in st.session_state:
        st.session_state.ota_registry = OTAServiceRegistry()
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🚗 AutoForge — Vehicle Health")
    with col2:
        variant = st.session_state.get("vehicle_variant", "ev").upper()
        st.markdown(f"### 🏭 {variant}")
    with col3:
        st.markdown("### 🟢 LIVE")
    
    # ---- Sidebar controls ----
    _render_sidebar()
    
    # Initialize simulator
    if "simulator" not in st.session_state:
        data_bridge.initialize_simulator()
    
    # Get current data
    current_state = data_bridge.get_next_tick()
    alerts = data_bridge.get_current_alerts()
    history_df = data_bridge.get_history()
    
    # Run predictive analysis
    predictions = st.session_state.predictive_engine.analyze(history_df)
    
    # ---- Alerts + Predictions ----
    col_alert, col_pred = st.columns(2)
    with col_alert:
        st.markdown("## 🚨 Active Alerts")
        render_alert_panel(alerts)
    with col_pred:
        st.markdown("## 🔮 Predictive Diagnostics")
        _render_predictions(predictions)
    
    st.markdown("---")
    
    # ---- Gauges ----
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
    
    # ---- Charts ----
    st.markdown("## 📈 Trend Charts")
    col1, col2 = st.columns(2)
    with col1:
        render_tyre_pressure_trend(history_df)
    with col2:
        render_battery_trend(history_df)
    
    col1, col2 = st.columns(2)
    with col1:
        render_speed_trend(history_df)
    with col2:
        render_temperature_trend(history_df)
    
    st.markdown("---")
    
    # ---- Bottom tabs ----
    st.markdown("## 📋 Detailed Views")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Raw Signals", "Alert Log", "Generated Code", "KPI Metrics", "OTA Registry"
    ])
    
    with tab1:
        st.subheader("Raw Signal Data")
        if not history_df.empty:
            display_df = history_df.tail(20).sort_values("timestamp", ascending=False)
            st.dataframe(display_df, hide_index=True)
        else:
            st.info("No signal data available yet")
    
    with tab2:
        st.subheader("Alert History")
        render_alert_history_table(alerts)
    
    with tab3:
        st.subheader("Generated Code Viewer")
        _render_code_viewer()
    
    with tab4:
        st.subheader("📊 KPI Metrics Dashboard")
        _render_kpi_panel()
    
    with tab5:
        st.subheader("📡 OTA Service Registry")
        _render_ota_tab()
    
    # Auto-refresh
    time.sleep(st.session_state.get("tick_speed", 0.5))
    st.rerun()


def _render_sidebar():
    """Render sidebar controls for the live dashboard."""
    # Vehicle variant
    st.sidebar.header("🏭 Vehicle Configuration")
    variant_options = {"ev": "⚡ EV", "hybrid": "🔋 Hybrid", "ice": "⛽ ICE"}
    selected = st.sidebar.selectbox(
        "Vehicle Variant", list(variant_options.keys()),
        format_func=lambda x: variant_options[x], index=0, key="vehicle_variant"
    )
    variant = get_variant(selected)
    st.sidebar.caption(variant.description)
    st.sidebar.markdown("---")
    
    # Scenario controls
    st.sidebar.header("🎮 Scenario Controls")
    scenario_names = list(SCENARIOS.keys())
    selected_scenario = st.sidebar.selectbox("Select Scenario", scenario_names, index=0, key="selected_scenario")
    if selected_scenario in SCENARIOS:
        st.sidebar.info(SCENARIOS[selected_scenario].description)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Apply", key="apply_btn"):
            data_bridge.apply_scenario(selected_scenario)
    with col2:
        if st.button("Reset", key="reset_btn"):
            data_bridge.reset_simulator()
    
    st.sidebar.markdown("---")
    st.sidebar.slider("Tick Speed (seconds)", 0.1, 2.0, 0.5, 0.1, key="tick_speed")
    
    # OTA services summary
    st.sidebar.markdown("---")
    st.sidebar.header("📡 OTA Services")
    if "ota_registry" in st.session_state:
        registry = st.session_state.ota_registry
        summary = registry.get_registry_summary()
        st.sidebar.metric("Active Services", summary["active"])


def _render_predictions(predictions):
    """Render predictive diagnostics panel."""
    if not predictions:
        st.success("🔮 No issues predicted — all systems trending normal")
        return
    for pred in predictions:
        if pred.severity == "CRITICAL":
            st.error(f"🔴 **{pred.signal_name}**: {pred.message}")
        elif pred.severity == "WARNING":
            st.warning(f"🟡 **{pred.signal_name}**: {pred.message}")
        else:
            st.info(f"🔵 **{pred.signal_name}**: {pred.message}")


def _render_code_viewer():
    """Display generated code from outputs folder."""
    outputs_path = "autoforge/outputs"
    if not os.path.exists(outputs_path):
        st.info("No generated code yet. Go to 🤖 Code Generator to create services.")
        return
    try:
        services = [d for d in os.listdir(outputs_path) if os.path.isdir(os.path.join(outputs_path, d))]
        if not services:
            st.info("No generated code yet. Go to 🤖 Code Generator to create services.")
            return
        selected = st.selectbox("Select Service", services, key="code_viewer_service")
        if selected:
            service_path = os.path.join(outputs_path, selected)
            files = [f for f in os.listdir(service_path) if os.path.isfile(os.path.join(service_path, f))]
            if files:
                selected_file = st.selectbox("Select File", files, key="code_viewer_file")
                if selected_file:
                    file_path = os.path.join(service_path, selected_file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                    ext = os.path.splitext(selected_file)[1]
                    lang_map = {".cpp": "cpp", ".h": "cpp", ".rs": "rust", ".kt": "kotlin", ".json": "json", ".txt": "text"}
                    st.code(content, language=lang_map.get(ext, "text"))
    except Exception as e:
        st.error(f"Error: {e}")


def _render_kpi_panel():
    """Display KPI metrics from generated services."""
    import json
    import pandas as pd
    
    outputs_path = "autoforge/outputs"
    if not os.path.exists(outputs_path):
        st.info("No KPI data yet. Generate services first.")
        return
    
    metrics = []
    for svc_dir in os.listdir(outputs_path):
        meta_path = os.path.join(outputs_path, svc_dir, "metadata.json")
        if os.path.isfile(meta_path):
            try:
                with open(meta_path) as f:
                    data = json.load(f)
                if "kpi_metrics" in data:
                    metrics.append({"service": data.get("service_name", svc_dir), **data["kpi_metrics"]})
            except Exception:
                pass
    
    if not metrics:
        st.info("No KPI data available.")
        return
    
    df = pd.DataFrame(metrics)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Gen Time", f"{df.get('generation_time_seconds', pd.Series([0])).mean():.1f}s")
    with col2:
        st.metric("Build Success", f"{df.get('build_success', pd.Series([0])).mean() * 100:.0f}%")
    with col3:
        st.metric("Avg Violations", f"{df.get('static_analysis_violations', pd.Series([0])).mean():.1f}")
    with col4:
        st.metric("Tests Generated", f"{df.get('test_generated', pd.Series([0])).mean() * 100:.0f}%")
    st.dataframe(df, hide_index=True)


def _render_ota_tab():
    """Render OTA service registry tab."""
    import pandas as pd
    
    if "ota_registry" not in st.session_state:
        st.session_state.ota_registry = OTAServiceRegistry()
    
    registry = st.session_state.ota_registry
    summary = registry.get_registry_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", summary["total_services"])
    with col2:
        st.metric("Active", summary["active"])
    with col3:
        st.metric("Inactive", summary["inactive"])
    
    if summary["services"]:
        st.dataframe(pd.DataFrame(summary["services"]), hide_index=True)
    else:
        st.info("No services registered yet. Generate some from the 🤖 Code Generator page.")


# ============================================================
# Streamlit page auto-discovery calls this file directly.
# ============================================================
render_live_dashboard()
