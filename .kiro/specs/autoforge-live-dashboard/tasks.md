# Implementation Plan: AutoForge Live Vehicle Dashboard

## Overview

This implementation plan breaks down the AutoForge Live Vehicle Dashboard into discrete coding tasks. The dashboard consists of three layers: simulation (vehicle signal generation), data bridge (state management), and presentation (Streamlit UI). Tasks are ordered to enable incremental validation, with testing sub-tasks placed close to their implementation counterparts.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `autoforge/dashboard/` and `autoforge/dashboard/simulation/`
  - Create all `__init__.py` files for Python package structure
  - Update `requirements.txt` with streamlit, plotly, pandas, numpy, hypothesis
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ] 2. Implement simulation layer core
  - [x] 2.1 Create VehicleSimulator class with initialization
    - Implement `__init__` method with scenario parameter
    - Initialize all 13 VSS signal state variables with realistic default values
    - Initialize internal state tracking variables (_scenario_state, _tick_count)
    - _Requirements: 1.1, 1.2_
  
  - [ ]* 2.2 Write property test for signal initialization bounds
    - **Property 1: Signal State Initialization Bounds**
    - **Validates: Requirements 1.2**
  
  - [x] 2.3 Implement VehicleSimulator tick method
    - Implement normal mode random walk logic for all signals
    - Apply signal-specific deltas (speed ±5 kmh, pressure ±1 kPa, battery -0.05%)
    - Implement battery-range coupling formula (ev_range = battery_soc * 5.0 with gear adjustments)
    - Return complete signal dictionary with VSS-style keys
    - _Requirements: 1.3, 1.4, 1.5, 1.6_
  
  - [ ]* 2.4 Write property tests for tick behavior
    - **Property 2: Tick Returns Complete Signal Dictionary**
    - **Validates: Requirements 1.3**
    - **Property 3: Normal Mode Bounded Updates**
    - **Validates: Requirements 1.4**
    - **Property 4: Battery-Range Proportional Relationship**
    - **Validates: Requirements 1.5**
    - **Property 5: Gear and Speed Affect Range Calculation**
    - **Validates: Requirements 1.6**
  
  - [ ]* 2.5 Write unit tests for VehicleSimulator core
    - Test initialization with different scenarios
    - Test tick returns all 13 signal keys
    - Test signal value clamping to valid ranges
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3. Implement alert generation system
  - [x] 3.1 Create Alert dataclass
    - Define Alert with signal_name, current_value, threshold_value, severity, message, timestamp fields
    - _Requirements: 3.10_
  
  - [x] 3.2 Implement VehicleSimulator get_alert_status method
    - Evaluate tyre pressure thresholds (WARNING < 180 kPa, CRITICAL < 150 kPa) for all four tyres
    - Evaluate battery SOC thresholds (WARNING < 20%, CRITICAL < 10%)
    - Evaluate motor temperature thresholds (WARNING > 100 C, CRITICAL > 115 C)
    - Evaluate coolant temperature thresholds (WARNING > 95 C, CRITICAL > 105 C)
    - Return list of Alert objects with descriptive messages
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_
  
  - [ ]* 3.3 Write property tests for alert generation
    - **Property 6: Alert Threshold Detection**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9**
    - **Property 7: Alert Structure Completeness**
    - **Validates: Requirements 3.10**
  
  - [ ]* 3.4 Write unit tests for alert edge cases
    - Test alerts at exact boundary values (20%, 10%, 180 kPa, 150 kPa, 100 C, 115 C, 95 C, 105 C)
    - Test multiple simultaneous alerts
    - Test alert message formatting
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

- [ ] 4. Checkpoint - Ensure simulation layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement fault scenario system
  - [x] 5.1 Create ScenarioDefinition dataclass and SCENARIOS dictionary
    - Define ScenarioDefinition with name, description, signal_overrides, signal_trends fields
    - Implement SCENARIOS dictionary with tyre_puncture, low_battery, overheating, highway_cruise, city_driving
    - Define scenario specifications (tyre_puncture: 220→80 kPa over 30 ticks, low_battery: 3x drain, overheating: 80→118 C over 20 ticks, highway_cruise: 120 kmh ±2, city_driving: 0-60 kmh oscillation)
    - _Requirements: 2.7_
  
  - [x] 5.2 Implement apply_scenario function
    - Accept VehicleSimulator instance and scenario_name
    - Apply signal_overrides immediately
    - Initialize signal_trends progression state
    - _Requirements: 2.8_
  
  - [x] 5.3 Implement VehicleSimulator trigger_scenario and reset methods
    - Implement trigger_scenario to call apply_scenario and update _scenario_state
    - Implement scenario progression logic in tick method (deterministic trend toward targets)
    - Implement reset method to clear scenario state and return to normal mode
    - Handle invalid scenario names with ValueError
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [ ]* 5.4 Write property test for scenario determinism
    - **Property 10: Scenario Determinism**
    - **Validates: Requirements 11.1, 11.3**
  
  - [ ]* 5.5 Write unit tests for specific scenarios
    - Test tyre_puncture reaches ~80 kPa after 30 ticks
    - Test low_battery triples drain rate
    - Test overheating reaches ~118 C after 20 ticks
    - Test highway_cruise maintains speed near 120 kmh
    - Test city_driving oscillates between 0-60 kmh
    - Test invalid scenario name raises ValueError
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 6. Implement data bridge layer
  - [x] 6.1 Create data_bridge module with state management functions
    - Implement initialize_simulator function using st.session_state
    - Implement get_next_tick function that calls simulator.tick() and appends to history buffer
    - Implement FIFO history buffer management (max 60 entries)
    - Implement get_history function that returns pandas DataFrame with timestamp column
    - Implement get_current_alerts function
    - Implement apply_scenario and reset_simulator functions
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [ ]* 6.2 Write property tests for history buffer
    - **Property 8: History Buffer Bounded Growth**
    - **Validates: Requirements 4.3, 4.4**
  
  - [ ]* 6.3 Write unit tests for data bridge
    - Test initialize_simulator creates simulator in session_state
    - Test history buffer FIFO eviction at 60 entries
    - Test get_history returns DataFrame with correct schema
    - Test empty history returns empty DataFrame
    - Test session_state recovery on corruption
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 7. Checkpoint - Ensure data bridge tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement gauge visualization components
  - [x] 8.1 Create gauge_components module with dark theme configuration
    - Define GAUGE_THEME dictionary with dark background (#0d1117) and styling
    - Define color range configurations for speedometer, tyre pressure, battery, temperature
    - _Requirements: 5.9, 5.10_
  
  - [x] 8.2 Implement gauge rendering functions
    - Implement render_speedometer with 0-200 kmh range and green/yellow/red zones
    - Implement render_tyre_pressure_gauge with 150-350 kPa range and red/green/yellow zones
    - Implement render_battery_gauge as horizontal bar with 0-100% range and red/yellow/green zones
    - Implement render_temperature_gauge as thermometer style with 20-120 C range
    - All gauges use Plotly with dark theme and 200px height
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_
  
  - [ ]* 8.3 Write unit tests for gauge components
    - Test gauge rendering with valid signal values
    - Test value clamping for out-of-range inputs
    - Test Plotly configuration matches theme requirements
    - Mock st.plotly_chart to verify rendering calls
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [ ] 9. Implement chart visualization components
  - [x] 9.1 Create chart_components module with dark theme configuration
    - Define CHART_THEME dictionary with dark background and styling
    - Define THRESHOLD_LINE_STYLE for warning lines
    - _Requirements: 6.8, 6.9_
  
  - [x] 9.2 Implement chart rendering functions
    - Implement render_tyre_pressure_trend with 4 line traces and 180 kPa threshold line
    - Implement render_battery_trend as area chart with dual Y-axes (soc % and range km)
    - Implement render_speed_trend as line chart
    - Implement render_temperature_trend with 2 traces and warning threshold lines (100 C, 95 C)
    - All charts use 60-tick rolling window and 300px height
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_
  
  - [ ]* 9.3 Write property test for chart display window
    - **Property 9: Chart Display Window Limit**
    - **Validates: Requirements 6.7**
  
  - [ ]* 9.4 Write unit tests for chart components
    - Test chart rendering with populated history DataFrame
    - Test chart rendering with empty history DataFrame
    - Test threshold lines appear at correct values
    - Mock st.plotly_chart to verify rendering calls
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ] 10. Implement alert display components
  - [x] 10.1 Create alert_components module
    - Implement render_alert_panel that displays alerts with severity-based styling (st.error for CRITICAL, st.warning for WARNING)
    - Implement render_alert_history_table that displays alerts as DataFrame
    - Format alert messages as "[SEVERITY] Signal: value (threshold: X) - Message"
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 10.2 Write unit tests for alert components
    - Test CRITICAL alerts use st.error styling
    - Test WARNING alerts use st.warning styling
    - Test alert message formatting
    - Test empty alert list displays no alerts
    - Mock Streamlit functions to verify calls
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 11. Checkpoint - Ensure component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement main dashboard application
  - [x] 12.1 Create app.py with page configuration and dark theme
    - Set page config with title "AutoForge — Vehicle Health", wide layout, expanded sidebar
    - Inject dark theme CSS for consistent styling
    - _Requirements: 8.1_
  
  - [x] 12.2 Implement header and sidebar
    - Implement render_header with logo and "🟢 LIVE" status indicator
    - Implement sidebar with scenario selector dropdown, Apply button, Reset button, tick speed slider
    - Implement render_generated_services_list that checks outputs folder and displays services or "No generated services available"
    - _Requirements: 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 12.1, 12.2_
  
  - [x] 12.3 Implement main content layout
    - Initialize simulator on first run using data_bridge.initialize_simulator
    - Implement continuous refresh loop with get_next_tick, get_current_alerts, get_history
    - Arrange alerts row at top
    - Arrange gauges row with 6 columns (speedometer, 4 tyre pressures, battery)
    - Arrange 2 chart rows (tyre pressure + battery, speed + temperature)
    - Implement bottom tabs for Raw Signals, Alert Log, Generated Code
    - Implement sleep based on tick_speed slider and st.rerun for continuous updates
    - _Requirements: 8.8, 8.9, 8.10_
  
  - [ ]* 12.4 Write integration tests for dashboard
    - Test dashboard initializes simulator on first load
    - Test scenario application updates simulator state
    - Test reset button reinitializes simulator
    - Test graceful degradation with empty outputs folder
    - Mock Streamlit components and verify layout structure
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 12.1, 12.2_

- [ ] 13. Create entry point script
  - [x] 13.1 Create run_dashboard.py
    - Check if streamlit is installed using importlib
    - If not installed, print installation instructions and exit with code 1
    - If installed, execute "streamlit run autoforge/dashboard/app.py" using subprocess
    - Print usage instructions to console
    - Handle file not found errors with helpful messages
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 13.2 Write unit tests for entry point
    - Test streamlit check with missing dependency
    - Test streamlit check with installed dependency
    - Test file not found error handling
    - Mock subprocess and importlib calls
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 14. Final checkpoint - Ensure all tests pass
  - Run complete test suite (unit tests and property tests)
  - Verify all 10 correctness properties pass with 100+ iterations
  - Ensure overall code coverage meets 85% minimum
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and error conditions
- Checkpoints ensure incremental validation at logical breaks
- The dashboard operates independently without requiring other AutoForge phases
- All visualizations use consistent dark theme (#0d1117 background)
- History buffer maintains 60-tick rolling window for performance
