"""Quick test to verify get_alert_status implementation."""

from autoforge.dashboard.simulation.vehicle_simulator import VehicleSimulator

# Test 1: Normal conditions - no alerts
print("Test 1: Normal conditions (no alerts expected)")
sim = VehicleSimulator()
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 0, "Expected no alerts in normal conditions"
print("  ✓ PASS\n")

# Test 2: Low tyre pressure - WARNING
print("Test 2: Low tyre pressure - WARNING")
sim = VehicleSimulator()
sim.tyre_pressure_fl = 170.0  # Below 180 kPa
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "WARNING", "Expected WARNING severity"
assert alerts[0].signal_name == "tyre_pressure_fl", "Expected tyre_pressure_fl"
assert alerts[0].threshold_value == 180.0, "Expected threshold 180.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 3: Critical tyre pressure
print("Test 3: Critical tyre pressure")
sim = VehicleSimulator()
sim.tyre_pressure_rr = 140.0  # Below 150 kPa
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "CRITICAL", "Expected CRITICAL severity"
assert alerts[0].signal_name == "tyre_pressure_rr", "Expected tyre_pressure_rr"
assert alerts[0].threshold_value == 150.0, "Expected threshold 150.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 4: Low battery - WARNING
print("Test 4: Low battery - WARNING")
sim = VehicleSimulator()
sim.battery_soc = 15.0  # Below 20%
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "WARNING", "Expected WARNING severity"
assert alerts[0].signal_name == "battery_soc", "Expected battery_soc"
assert alerts[0].threshold_value == 20.0, "Expected threshold 20.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 5: Critical battery
print("Test 5: Critical battery")
sim = VehicleSimulator()
sim.battery_soc = 5.0  # Below 10%
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "CRITICAL", "Expected CRITICAL severity"
assert alerts[0].signal_name == "battery_soc", "Expected battery_soc"
assert alerts[0].threshold_value == 10.0, "Expected threshold 10.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 6: High motor temperature - WARNING
print("Test 6: High motor temperature - WARNING")
sim = VehicleSimulator()
sim.motor_temperature = 105.0  # Above 100 C
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "WARNING", "Expected WARNING severity"
assert alerts[0].signal_name == "motor_temperature", "Expected motor_temperature"
assert alerts[0].threshold_value == 100.0, "Expected threshold 100.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 7: Critical motor temperature
print("Test 7: Critical motor temperature")
sim = VehicleSimulator()
sim.motor_temperature = 118.0  # Above 115 C
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "CRITICAL", "Expected CRITICAL severity"
assert alerts[0].signal_name == "motor_temperature", "Expected motor_temperature"
assert alerts[0].threshold_value == 115.0, "Expected threshold 115.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 8: High coolant temperature - WARNING
print("Test 8: High coolant temperature - WARNING")
sim = VehicleSimulator()
sim.coolant_temperature = 100.0  # Above 95 C
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "WARNING", "Expected WARNING severity"
assert alerts[0].signal_name == "coolant_temperature", "Expected coolant_temperature"
assert alerts[0].threshold_value == 95.0, "Expected threshold 95.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 9: Critical coolant temperature
print("Test 9: Critical coolant temperature")
sim = VehicleSimulator()
sim.coolant_temperature = 108.0  # Above 105 C
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 1, "Expected 1 alert"
assert alerts[0].severity == "CRITICAL", "Expected CRITICAL severity"
assert alerts[0].signal_name == "coolant_temperature", "Expected coolant_temperature"
assert alerts[0].threshold_value == 105.0, "Expected threshold 105.0"
print(f"  Message: {alerts[0].message}")
print("  ✓ PASS\n")

# Test 10: Multiple alerts
print("Test 10: Multiple alerts")
sim = VehicleSimulator()
sim.tyre_pressure_fl = 170.0  # WARNING
sim.tyre_pressure_fr = 140.0  # CRITICAL
sim.battery_soc = 5.0  # CRITICAL
sim.motor_temperature = 118.0  # CRITICAL
alerts = sim.get_alert_status()
print(f"  Alerts: {len(alerts)}")
assert len(alerts) == 4, "Expected 4 alerts"
print("  Messages:")
for alert in alerts:
    print(f"    [{alert.severity}] {alert.message}")
print("  ✓ PASS\n")

# Test 11: Alert structure completeness
print("Test 11: Alert structure completeness")
sim = VehicleSimulator()
sim.battery_soc = 5.0
alerts = sim.get_alert_status()
alert = alerts[0]
assert hasattr(alert, 'signal_name'), "Alert missing signal_name"
assert hasattr(alert, 'current_value'), "Alert missing current_value"
assert hasattr(alert, 'threshold_value'), "Alert missing threshold_value"
assert hasattr(alert, 'severity'), "Alert missing severity"
assert hasattr(alert, 'message'), "Alert missing message"
assert hasattr(alert, 'timestamp'), "Alert missing timestamp"
assert alert.current_value == 5.0, "Current value should match battery_soc"
print("  ✓ PASS\n")

print("=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
