# Requirements Document

## Introduction

The AutoForge Live Vehicle Dashboard is a real-time visualization system that demonstrates the vehicle health monitoring capabilities of the AutoForge platform. The system simulates Vehicle Signal Specification (VSS) compliant signals, applies fault scenarios, and displays vehicle health data through an interactive web dashboard built with Streamlit.

This feature integrates with the existing AutoForge ecosystem (RAG Knowledge Base, Multi-Agent Code Generation, and Self-Healing Build) by providing a live demonstration environment and visualizing the generated services.

## Glossary

- **Vehicle_Simulator**: Component that maintains and updates simulated VSS signal values
- **VSS_Signal**: A Vehicle Signal Specification compliant data point (e.g., vehicle_speed, tyre_pressure_fl)
- **Fault_Scenario**: A predefined pattern of signal changes that simulates vehicle malfunctions
- **Alert**: A notification generated when a VSS_Signal exceeds defined thresholds
- **Dashboard**: The Streamlit web application that visualizes vehicle health data
- **Tick**: A single simulation time step that updates all VSS_Signal values
- **Data_Bridge**: Component that manages state between the Vehicle_Simulator and Dashboard
- **Gauge**: A visual component displaying a single VSS_Signal value
- **Trend_Chart**: A time-series visualization showing VSS_Signal history
- **Alert_Panel**: A visual component displaying current Alert messages
- **Scenario_Selector**: UI control for choosing and applying Fault_Scenarios

## Requirements

### Requirement 1: Vehicle Signal Simulation

**User Story:** As a developer, I want to simulate realistic vehicle signals, so that I can demonstrate vehicle health monitoring without physical hardware.

#### Acceptance Criteria

1. THE Vehicle_Simulator SHALL maintain state for ten VSS_Signals: vehicle_speed (0-200 kmh), tyre_pressure_fl (150-350 kPa), tyre_pressure_fr (150-350 kPa), tyre_pressure_rl (150-350 kPa), tyre_pressure_rr (150-350 kPa), battery_soc (0-100%), ev_range (0-500 km), throttle_position (0-100%), brake_position (0-100%), gear_position (0-8), steering_angle (-540 to 540 degrees), motor_temperature (20-120 C), coolant_temperature (20-110 C)
2. WHEN the Vehicle_Simulator is initialized with a scenario parameter, THE Vehicle_Simulator SHALL set realistic initial values for all VSS_Signals
3. WHEN the tick method is called, THE Vehicle_Simulator SHALL update all VSS_Signal values and return them as a dictionary with VSS-style keys
4. WHEN operating in normal mode, THE Vehicle_Simulator SHALL apply random walk updates with vehicle_speed changing by ±5 kmh, tyre_pressure changing by ±1 kPa, and battery_soc draining by 0.05% per tick
5. WHEN battery_soc changes, THE Vehicle_Simulator SHALL update ev_range proportionally to battery_soc
6. WHEN gear_position or vehicle_speed changes, THE Vehicle_Simulator SHALL adjust ev_range calculations accordingly

### Requirement 2: Fault Scenario Injection

**User Story:** As a developer, I want to inject predefined fault scenarios, so that I can demonstrate how the system detects and alerts on vehicle malfunctions.

#### Acceptance Criteria

1. THE Vehicle_Simulator SHALL support a trigger_scenario method that accepts a scenario_name parameter
2. WHEN trigger_scenario is called with "tyre_puncture", THE Vehicle_Simulator SHALL reduce tyre_pressure_fl from 220 kPa to 80 kPa over 30 ticks
3. WHEN trigger_scenario is called with "low_battery", THE Vehicle_Simulator SHALL triple the battery_soc drain rate
4. WHEN trigger_scenario is called with "overheating", THE Vehicle_Simulator SHALL increase motor_temperature from 80 C to 118 C over 20 ticks
5. WHEN trigger_scenario is called with "highway_cruise", THE Vehicle_Simulator SHALL maintain vehicle_speed at 120 kmh with minimal variation
6. WHEN trigger_scenario is called with "city_driving", THE Vehicle_Simulator SHALL oscillate vehicle_speed between 0 and 60 kmh
7. THE Fault_Scenario system SHALL provide a SCENARIOS dictionary containing scenario definitions with description, signal_overrides, and signal_trends fields
8. THE Fault_Scenario system SHALL provide an apply_scenario function that accepts a Vehicle_Simulator instance and scenario_name

### Requirement 3: Alert Generation

**User Story:** As a vehicle operator, I want to receive alerts when signals exceed safe thresholds, so that I can respond to potential vehicle issues.

#### Acceptance Criteria

1. THE Vehicle_Simulator SHALL provide a get_alert_status method that returns a list of Alert objects
2. WHEN tyre_pressure for any tyre is below 180 kPa, THE Vehicle_Simulator SHALL generate a WARNING severity Alert
3. WHEN tyre_pressure for any tyre is below 150 kPa, THE Vehicle_Simulator SHALL generate a CRITICAL severity Alert
4. WHEN battery_soc is below 20%, THE Vehicle_Simulator SHALL generate a WARNING severity Alert
5. WHEN battery_soc is below 10%, THE Vehicle_Simulator SHALL generate a CRITICAL severity Alert
6. WHEN motor_temperature exceeds 100 C, THE Vehicle_Simulator SHALL generate a WARNING severity Alert
7. WHEN motor_temperature exceeds 115 C, THE Vehicle_Simulator SHALL generate a CRITICAL severity Alert
8. WHEN coolant_temperature exceeds 95 C, THE Vehicle_Simulator SHALL generate a WARNING severity Alert
9. WHEN coolant_temperature exceeds 105 C, THE Vehicle_Simulator SHALL generate a CRITICAL severity Alert
10. FOR EACH Alert, THE Vehicle_Simulator SHALL include signal name, current value, threshold value, severity level, and descriptive message

### Requirement 4: Dashboard State Management

**User Story:** As a dashboard developer, I want centralized state management, so that the simulation state persists across Streamlit reruns.

#### Acceptance Criteria

1. THE Data_Bridge SHALL use Streamlit session_state for Vehicle_Simulator persistence
2. THE Data_Bridge SHALL provide an initialize_simulator function that accepts a scenario parameter
3. THE Data_Bridge SHALL provide a get_next_tick function that calls Vehicle_Simulator tick and appends results to a history buffer
4. THE Data_Bridge SHALL maintain a history buffer with a maximum of 60 ticks
5. THE Data_Bridge SHALL provide a get_history function that returns a pandas DataFrame with timestamp column
6. THE Data_Bridge SHALL provide a get_current_alerts function that returns the current Alert list

### Requirement 5: Real-Time Gauge Visualization

**User Story:** As a vehicle operator, I want to see current signal values on gauges, so that I can quickly assess vehicle status.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a speedometer gauge displaying vehicle_speed with a maximum value of 200 kmh
2. THE speedometer gauge SHALL use green color for 0-80 kmh, yellow for 80-130 kmh, and red for 130-200 kmh
3. THE Dashboard SHALL provide tyre_pressure_gauge components for each of the four tyres
4. THE tyre_pressure_gauge SHALL use red color below 180 kPa, green for 180-280 kPa, and yellow for 280-350 kPa
5. THE Dashboard SHALL provide a battery_gauge displaying battery_soc as a horizontal bar
6. THE battery_gauge SHALL use red color for 0-20%, yellow for 20-40%, and green for 40-100%
7. THE Dashboard SHALL provide temperature_gauge components for motor_temperature and coolant_temperature
8. THE temperature_gauge SHALL display values in thermometer style with a maximum value of 120 C
9. ALL gauge components SHALL use dark theme with background color #0d1117, white text, and no borders
10. ALL gauge components SHALL render with a height of 200 pixels

### Requirement 6: Trend Chart Visualization

**User Story:** As a vehicle operator, I want to see signal trends over time, so that I can identify patterns and predict issues.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a tyre_pressure_trend chart displaying all four tyre pressures as line series
2. THE tyre_pressure_trend chart SHALL display a red threshold line at 180 kPa
3. THE Dashboard SHALL provide a battery_trend chart with dual Y-axes for battery_soc and ev_range
4. THE battery_trend chart SHALL render as an area chart
5. THE Dashboard SHALL provide a vehicle_speed_trend chart displaying vehicle_speed as a line series
6. THE Dashboard SHALL provide a temperature_trend chart displaying motor_temperature and coolant_temperature with warning threshold lines
7. ALL trend charts SHALL display a rolling window of 60 ticks
8. ALL trend charts SHALL use dark theme styling
9. ALL trend charts SHALL render with a height of 300 pixels

### Requirement 7: Alert Display

**User Story:** As a vehicle operator, I want to see active alerts prominently, so that I can respond to critical issues immediately.

#### Acceptance Criteria

1. THE Dashboard SHALL provide an alert_panel component that accepts an Alert list
2. WHEN an Alert has CRITICAL severity, THE alert_panel SHALL display it using Streamlit error styling
3. WHEN an Alert has WARNING severity, THE alert_panel SHALL display it using Streamlit warning styling
4. THE Dashboard SHALL provide an alert_history_table component that displays past Alert records
5. THE alert_history_table SHALL render as a Streamlit dataframe

### Requirement 8: Interactive Dashboard Interface

**User Story:** As a user, I want an interactive dashboard with scenario controls, so that I can explore different vehicle conditions.

#### Acceptance Criteria

1. THE Dashboard SHALL use dark theme with page title "AutoForge — Vehicle Health" and wide layout
2. THE Dashboard SHALL display a header with logo and live status indicator showing "🟢 LIVE"
3. THE Dashboard SHALL provide a sidebar containing Scenario_Selector, Apply button, Reset button, and tick speed slider
4. THE Scenario_Selector SHALL list all available Fault_Scenarios
5. WHEN the Apply button is clicked, THE Dashboard SHALL apply the selected Fault_Scenario to the Vehicle_Simulator
6. WHEN the Reset button is clicked, THE Dashboard SHALL reinitialize the Vehicle_Simulator to normal mode
7. THE Dashboard SHALL display the Generated Services list in the sidebar
8. THE Dashboard SHALL arrange the main content area with alerts row, gauges row with 6 columns, and 2 chart rows
9. THE Dashboard SHALL provide bottom tabs for Raw Signals view, Alert Log view, and Generated Code viewer
10. THE Dashboard SHALL auto-refresh using a continuous loop with configurable sleep interval based on tick speed slider

### Requirement 9: Application Entry Point

**User Story:** As a user, I want a simple command to launch the dashboard, so that I can start the application easily.

#### Acceptance Criteria

1. THE Application SHALL provide a run_dashboard.py entry point script
2. WHEN run_dashboard.py is executed, THE Application SHALL check if streamlit is installed
3. IF streamlit is not installed, THEN THE Application SHALL display installation instructions and exit
4. WHEN streamlit is installed, THE Application SHALL execute the command "streamlit run autoforge/dashboard/app.py"
5. THE Application SHALL print usage instructions to the console

### Requirement 10: Dependency Management

**User Story:** As a developer, I want all dependencies documented, so that I can install the required packages.

#### Acceptance Criteria

1. THE Application SHALL include streamlit in requirements.txt
2. THE Application SHALL include plotly in requirements.txt
3. THE Application SHALL include pandas in requirements.txt
4. THE Application SHALL include numpy in requirements.txt

### Requirement 11: Deterministic Fault Progression

**User Story:** As a developer, I want fault scenarios to progress predictably, so that demonstrations are reliable and reproducible.

#### Acceptance Criteria

1. WHEN a Fault_Scenario is applied, THE Vehicle_Simulator SHALL progress the fault in a deterministic manner
2. THE Vehicle_Simulator SHALL make fault effects visible within 10 seconds of real time
3. THE Vehicle_Simulator SHALL use numpy for random walk calculations to ensure reproducibility with seed control

### Requirement 12: Graceful Degradation

**User Story:** As a user, I want the dashboard to work even without generated code, so that I can use it standalone.

#### Acceptance Criteria

1. WHEN the outputs folder is empty, THE Dashboard SHALL display a message indicating no generated services are available
2. WHEN the outputs folder is empty, THE Dashboard SHALL continue to function with simulation and visualization features
3. THE Dashboard SHALL operate independently without requiring Phase 2 or Phase 3 components

## Notes

This feature builds upon the existing AutoForge ecosystem:
- Phase 1: RAG Knowledge Base provides VSS documentation context
- Phase 2: Multi-Agent Code Generation creates vehicle service implementations
- Phase 3: Self-Healing Build ensures generated code quality
- Phase 4 (this feature): Live Dashboard demonstrates the complete system in action

The dashboard serves as both a demonstration tool and a testing environment for the generated vehicle services.
