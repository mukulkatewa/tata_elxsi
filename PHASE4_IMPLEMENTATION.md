# Phase 4: Live Vehicle Dashboard - Implementation Summary

## Overview

Phase 4 implements a real-time vehicle health monitoring dashboard that demonstrates the AutoForge platform's capabilities through simulated Vehicle Signal Specification (VSS) compliant data. The system consists of three architectural layers: simulation, data bridge, and presentation.

## Technical Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│              Presentation Layer                         │
│  (Streamlit UI - Gauges, Charts, Alerts)               │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│              Data Bridge Layer                          │
│  (State Management - session_state, History Buffer)    │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│              Simulation Layer                           │
│  (VehicleSimulator - Signal Generation, Scenarios)     │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**Simulation Layer**: Generates realistic vehicle signals and applies fault scenarios
- `VehicleSimulator`: Maintains 13 VSS signal state variables
- `scenarios.py`: Defines fault patterns and driving scenarios
- Implements deterministic fault progression
- Evaluates alert thresholds

**Data Bridge Layer**: Manages state persistence and data flow
- Uses Streamlit `session_state` for simulator persistence
- Maintains 60-tick rolling history buffer (FIFO)
- Converts history to pandas DataFrame for visualization
- Provides clean API between simulation and UI

**Presentation Layer**: Renders interactive visualizations
- Streamlit app with dark theme (#0d1117 background)
- Plotly gauges and charts with consistent styling
- Real-time updates via continuous refresh loop
- Sidebar controls for scenario injection

## File Structure

```
autoforge/
├── dashboard/
│   ├── __init__.py
│   ├── app.py                          # Main Streamlit application
│   ├── data_bridge.py                  # State management layer
│   ├── components/
│   │   ├── __init__.py
│   │   ├── alerts.py                   # Alert display components
│   │   ├── charts.py                   # Trend chart components
│   │   └── gauges.py                   # Gauge visualization components
│   └── simulation/
│       ├── __init__.py
│       ├── scenarios.py                # Fault scenario definitions
│       └── vehicle_simulator.py        # VehicleSimulator class
│
├── outputs/                            # Generated services (optional)
│
run_dashboard.py                        # Entry point script
requirements.txt                        # Dependencies (streamlit, plotly, pandas, numpy)
```

## Core Components

### VehicleSimulator Class

**Location**: `autoforge/dashboard/simulation/vehicle_simulator.py`

**Responsibilities**:
- Maintain state for 13 VSS signals
- Update signals via `tick()` method
- Generate alerts via `get_alert_status()`
- Apply fault scenarios via `trigger_scenario()`
- Reset to normal mode via `reset()`

**VSS Signals** (13 total):
- `vehicle_speed`: 0-200 km/h
- `tyre_pressure_fl/fr/rl/rr`: 150-350 kPa (four tyres)
- `battery_soc`: 0-100%
- `ev_range`: 0-500 km (calculated from battery and gear)
- `throttle_position`: 0-100%
- `brake_position`: 0-100%
- `gear_position`: 0-8 (integer)
- `steering_angle`: -540 to 540 degrees
- `motor_temperature`: 20-120°C
- `coolant_temperature`: 20-110°C

**Update Logic**:
- **Normal mode**: Random walk with signal-specific deltas
  - Speed: ±5 km/h per tick
  - Tyre pressure: ±1 kPa per tick
  - Battery: -0.05% per tick (drain)
- **Scenario mode**: Deterministic progression toward target values
  - Linear interpolation: `delta = (target - current) / remaining_ticks`
  - Ensures predictable fault progression

**Battery-Range Coupling**:
```python
base_range = battery_soc * 5.0
gear_factor = 0.5 (gear 0) | 0.7 (gear 1-2) | 1.0 (gear 3-4) | 1.1 (gear 5+)
speed_factor = 0.8 (>130 km/h) | 0.9 (>100 km/h) | 1.0 (≤100 km/h)
ev_range = base_range * gear_factor * speed_factor
```

### Scenarios Module

**Location**: `autoforge/dashboard/simulation/scenarios.py`

**ScenarioDefinition Structure**:
```python
@dataclass
class ScenarioDefinition:
    name: str
    description: str
    signal_overrides: Dict[str, float]      # Immediate changes
    signal_trends: Dict[str, Tuple[float, int]]  # (target, ticks)
```

**Available Scenarios**:

1. **normal**: Baseline operation with random walk
2. **tyre_puncture**: FL pressure 220→80 kPa over 30 ticks
3. **low_battery**: 3x drain rate (-0.15% per tick)
4. **overheating**: Motor temp 80→118°C over 20 ticks
5. **highway_cruise**: Speed locked at 120 km/h (±2 km/h)
6. **city_driving**: Speed oscillates 0-60 km/h (15-tick period)

**Application Logic**:
- `signal_overrides`: Applied immediately at tick 0
- `signal_trends`: Progressive updates over N ticks
- Stored in `simulator._scenario_state` for tick-by-tick progression

### Alert System

**Alert Thresholds**:

| Signal | WARNING | CRITICAL |
|--------|---------|----------|
| Tyre Pressure | < 180 kPa | < 150 kPa |
| Battery SOC | < 20% | < 10% |
| Motor Temp | > 100°C | > 115°C |
| Coolant Temp | > 95°C | > 105°C |

**Alert Data Model**:
```python
@dataclass
class Alert:
    signal_name: str
    current_value: float
    threshold_value: float
    severity: str  # "WARNING" or "CRITICAL"
    message: str
    timestamp: datetime
```

**Generation**: `VehicleSimulator.get_alert_status()` evaluates all thresholds each tick and returns a list of active alerts.

### Data Bridge Module

**Location**: `autoforge/dashboard/data_bridge.py`

**Key Functions**:
- `initialize_simulator(scenario)`: Create simulator in `st.session_state`
- `get_next_tick()`: Call `simulator.tick()`, append to history, return state
- `get_history()`: Return history as pandas DataFrame with timestamps
- `get_current_alerts()`: Return alert list from simulator
- `apply_scenario(name)`: Trigger scenario on simulator
- `reset_simulator()`: Reinitialize to normal mode

**Session State Schema**:
```python
st.session_state = {
    "simulator": VehicleSimulator,
    "history": List[Dict],  # Max 60 entries (FIFO)
    "tick_count": int,
    "start_time": datetime,
    "tick_speed": float,
    "selected_scenario": str,
    "alert_log": List[Alert]
}
```

**History Buffer Management**:
- Maximum 60 entries (rolling window)
- FIFO eviction when full
- Each entry: `{timestamp: datetime, **signal_values}`
- Converted to DataFrame for chart rendering

### Visualization Components

**Gauge Components** (`components/gauges.py`):
- `render_speedometer()`: 0-200 km/h with green/yellow/red zones
- `render_tyre_pressure_gauge()`: 150-350 kPa with red/green/yellow zones
- `render_battery_gauge()`: 0-100% horizontal bar with red/yellow/green zones
- `render_temperature_gauge()`: 20-120°C thermometer style

**Chart Components** (`components/charts.py`):
- `render_tyre_pressure_trend()`: 4 line traces + 180 kPa threshold
- `render_battery_trend()`: Dual Y-axis area chart (SOC % + range km)
- `render_speed_trend()`: Single line trace
- `render_temperature_trend()`: 2 traces + warning thresholds (100°C, 95°C)

**Alert Components** (`components/alerts.py`):
- `render_alert_panel()`: Display active alerts with severity styling
- `render_alert_history_table()`: Historical alert DataFrame

**Theme Configuration**:
```python
DARK_THEME = {
    "paper_bgcolor": "#0d1117",
    "plot_bgcolor": "#0d1117",
    "font": {"color": "white"},
    "height": 200  # gauges
    "height": 300  # charts
}
```

### Main Application

**Location**: `autoforge/dashboard/app.py`

**Page Configuration**:
```python
st.set_page_config(
    page_title="AutoForge — Vehicle Health",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

**Layout Structure**:
1. **Header**: Logo + "🟢 LIVE" status indicator
2. **Sidebar**: Scenario controls + generated services list
3. **Alerts Row**: Active alerts at top
4. **Gauges Row**: 6 columns (speedometer, 4 tyres, battery)
5. **Chart Rows**: 2 rows with 2 charts each
6. **Bottom Tabs**: Raw Signals | Alert Log | Generated Code

**Refresh Loop**:
```python
while True:
    current_state = get_next_tick()
    alerts = get_current_alerts()
    history_df = get_history()
    
    # Render all components
    render_alert_panel(alerts)
    render_gauges(current_state)
    render_charts(history_df)
    
    time.sleep(st.session_state.get("tick_speed", 1.0))
    st.rerun()
```

### Entry Point Script

**Location**: `run_dashboard.py`

**Functionality**:
- Check if streamlit is installed (via `importlib.util.find_spec`)
- Print installation instructions if missing
- Verify `autoforge/dashboard/app.py` exists
- Execute: `streamlit run autoforge/dashboard/app.py`
- Handle errors gracefully with helpful messages

## Key Design Decisions

### Separation of Concerns

**Why**: Clear boundaries enable independent testing and maintenance
- Simulation logic isolated from UI rendering
- State management decoupled from both layers
- Components can be tested in isolation

### Streamlit Session State

**Why**: Native persistence across reruns without external database
- Simulator instance persists between UI updates
- History buffer maintained automatically
- No need for Redis or file-based storage

### Dark Theme Consistency

**Why**: Professional appearance and reduced eye strain
- All visualizations use #0d1117 background
- Consistent color palette across gauges and charts
- Matches modern development tool aesthetics

### 60-Tick Rolling Window

**Why**: Balance between history visibility and performance
- 60 ticks ≈ 1-2 minutes of data at default speed
- Prevents memory growth over long sessions
- Sufficient for trend analysis

### Deterministic Fault Progression

**Why**: Reliable demonstrations and reproducible testing
- Linear interpolation ensures predictable behavior
- Faults visible within 10-30 seconds
- No random failures during presentations

### Graceful Degradation

**Why**: Dashboard works standalone without other phases
- Checks for outputs folder before listing services
- Displays helpful message if empty
- All core features function independently

## Integration with AutoForge Ecosystem

### Phase 1: RAG Knowledge Base
- Provides VSS documentation context
- Knowledge base used during Phase 2 code generation
- Dashboard demonstrates VSS compliance

### Phase 2: Multi-Agent Code Generation
- Generated services appear in sidebar list
- Dashboard can visualize generated code in bottom tab
- Demonstrates end-to-end workflow

### Phase 3: Self-Healing Build
- Ensures generated code quality before deployment
- Dashboard benefits from validated services
- Build system prevents broken code from reaching dashboard

### Phase 4: Live Dashboard (This Phase)
- Brings everything together in interactive demo
- Real-time visualization of vehicle health
- Demonstrates complete AutoForge capabilities

## Testing Strategy

### Unit Tests
- VehicleSimulator initialization and tick behavior
- Scenario application and progression
- Alert threshold detection
- Data bridge state management
- Component rendering (with mocked Streamlit)

### Property-Based Tests
- Signal bounds after initialization (Property 1)
- Tick returns complete dictionary (Property 2)
- Normal mode bounded updates (Property 3)
- Battery-range relationship (Property 4)
- Gear/speed affect range (Property 5)
- Alert threshold detection (Property 6)
- Alert structure completeness (Property 7)
- History buffer bounded growth (Property 8)
- Chart display window limit (Property 9)
- Scenario determinism (Property 10)

### Integration Tests
- End-to-end dashboard initialization
- Scenario application through UI
- Reset functionality
- Graceful degradation with missing outputs

**Test Configuration**:
- Library: `hypothesis` for property-based testing
- Minimum 100 iterations per property test
- Coverage goal: 85% overall, 95% simulation layer

## Dependencies

**Core Requirements** (from `requirements.txt`):
- `streamlit`: Web application framework
- `plotly`: Interactive visualizations
- `pandas`: Data manipulation and DataFrame support
- `numpy`: Numerical operations and random walk

**Development Requirements**:
- `pytest`: Unit testing framework
- `hypothesis`: Property-based testing library

## Performance Considerations

### Memory Management
- History buffer capped at 60 entries (FIFO)
- Old entries automatically evicted
- No unbounded growth over long sessions

### Update Frequency
- Default: 1 tick per second
- Configurable via slider: 0.1 - 2.0 seconds
- Faster speeds for development, slower for presentations

### Rendering Optimization
- Plotly charts reuse configuration objects
- DataFrame conversion only when needed
- Minimal recomputation between ticks

## Error Handling

### Simulation Layer
- Signal values clamped to valid ranges
- Invalid scenario names raise `ValueError`
- Graceful fallback to normal mode on errors

### Data Bridge Layer
- Session state corruption triggers reinitialization
- Empty history returns empty DataFrame with correct schema
- Missing keys handled with defaults

### Presentation Layer
- Missing outputs folder displays helpful message
- Chart rendering wrapped in try-except blocks
- Invalid gauge values clamped before rendering

### Entry Point
- Checks for streamlit installation before launch
- Verifies app.py exists before execution
- Clear error messages with installation instructions

## Future Enhancements

### Potential Additions
- Export signal data to CSV
- Custom scenario builder UI
- Historical scenario replay
- Multi-vehicle comparison view
- WebSocket integration for real hardware
- Configurable alert thresholds
- Scenario scheduling (auto-apply at intervals)

### Scalability Considerations
- Current design supports single vehicle
- Could extend to fleet monitoring with minimal changes
- Database backend for long-term history
- Real-time streaming with Kafka/MQTT

## Conclusion

Phase 4 completes the AutoForge platform by providing an interactive demonstration environment. The three-layer architecture ensures maintainability, the dark theme provides professional aesthetics, and the fault scenario system enables compelling demonstrations of vehicle health monitoring capabilities.

The dashboard operates independently while integrating seamlessly with the broader AutoForge ecosystem, making it both a standalone tool and a capstone demonstration of the complete platform.
