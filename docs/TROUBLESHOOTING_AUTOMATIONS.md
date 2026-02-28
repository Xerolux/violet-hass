# Troubleshooting Automations for Violet Pool Controller

This document provides ready-to-use automation examples for monitoring and troubleshooting the Violet Pool Controller integration.

## Table of Contents

- [Connection Monitoring](#connection-monitoring)
- [Error Handling & Recovery](#error-handling--recovery)
- [Performance Monitoring](#performance-monitoring)
- [Diagnostic Automations](#diagnostic-automations)
- [Alert Notifications](#alert-notifications)

---

## Connection Monitoring

### 1. Monitor Controller Availability

```yaml
- alias: "Pool: Monitor Controller Availability"
  id: "pool_monitor_availability"
  description: "Track when controller goes offline/online"
  trigger:
    - platform: state
      entity_id: binary_sensor.pool_controller_status
      to: "off"
      for:
        minutes: 5
    - platform: state
      entity_id: binary_sensor.pool_controller_status
      to: "on"
      for:
        minutes: 2
  action:
    - choose:
        - conditions:
            - condition: state
              entity_id: binary_sensor.pool_controller_status
              state: "off"
          sequence:
            - service: notify.mobile_app_your_phone
              data:
                title: "⚠️ Pool Controller Offline"
                message: "The Violet pool controller has been offline for 5 minutes. Check network connectivity."
                data:
                  push:
                    sound: default
                    badge: 1
        - conditions:
            - condition: state
              entity_id: binary_sensor.pool_controller_status
              state: "on"
          sequence:
            - service: notify.mobile_app_your_phone
              data:
                title: "✅ Pool Controller Online"
                message: "The Violet pool controller is back online."
                data:
                  push:
                    sound: default
```

### 2. Test Connection Periodically

```yaml
- alias: "Pool: Test Connection Hourly"
  id: "pool_test_connection"
  description: "Test connection to controller every hour"
  trigger:
    - platform: time_pattern
      hours: "*"
  condition:
    - condition: state
      entity_id: binary_sensor.pool_controller_status
      state: "on"
  action:
    - service: violet_pool_controller.test_connection
      target:
        device_id: YOUR_DEVICE_ID
      response_variable: connection_test
    - choose:
        - conditions:
            - condition: template
              value_template: "{{ not connection_test.success }}"
          sequence:
            - service: notify.mobile_app_your_phone
              data:
                title: "❌ Pool Connection Test Failed"
                message: "Connection test failed: {{ connection_test.tests[0].message }}"
```

---

## Error Handling & Recovery

### 3. Automatic Error Summary on Failures

```yaml
- alias: "Pool: Get Error Summary on Failure"
  id: "pool_error_summary"
  description: "Retrieve error summary when errors occur"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pool_consecutive_errors
      above: 3
  action:
    - service: violet_pool_controller.get_error_summary
      target:
        device_id: YOUR_DEVICE_ID
      data:
        include_history: true
      response_variable: error_data
    - service: notify.mobile_app_your_phone
      data:
        title: "⚠️ Pool Controller Errors Detected"
        message: |
          Consecutive errors: {{ error_data.devices[0].error_summary.consecutive_errors }}
          Total errors: {{ error_data.devices[0].error_summary.total_errors }}
          Offline duration: {{ error_data.devices[0].error_summary.offline_duration_seconds | int }} seconds
          Recovery suggestion: {{ error_data.devices[0].recovery_suggestion }}
```

### 4. Clear Error History After Recovery

```yaml
- alias: "Pool: Clear Errors After Recovery"
  id: "pool_clear_errors"
  description: "Clear error history after successful recovery"
  trigger:
    - platform: state
      entity_id: sensor.pool_consecutive_errors
      from: "0"
      to: "0"
      for:
        minutes: 10
  condition:
    - condition: state
      entity_id: binary_sensor.pool_controller_status
      state: "on"
  action:
    - service: violet_pool_controller.clear_error_history
      target:
        device_id: YOUR_DEVICE_ID
    - service: logger.log
      data:
        message: "Pool controller: Error history cleared after successful recovery"
        level: info
```

### 5. Re-authentication Prompt

```yaml
- alias: "Pool: Prompt Re-authentication"
  id: "pool_reauth_prompt"
  description: "Notify when re-authentication is needed"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pool_auth_errors
      above: 2
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "🔐 Pool Controller: Re-authentication Required"
        message: "The pool controller is reporting authentication errors. Please reconfigure the integration with correct credentials."
        data:
          url: "/config/devices/dashboard?integrations=violet_pool_controller"
```

---

## Performance Monitoring

### 6. Monitor Connection Latency

```yaml
- alias: "Pool: High Latency Alert"
  id: "pool_latency_alert"
  description: "Alert when connection latency is too high"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pool_connection_latency
      above: 5000
      for:
        minutes: 5
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "⏱️ Pool Controller: High Latency"
        message: "Connection latency is {{ states('sensor.pool_connection_latency') }}ms. This may indicate network issues or controller overload."
```

### 7. Monitor System Health

```yaml
- alias: "Pool: Low System Health Alert"
  id: "pool_health_alert"
  description: "Alert when system health drops below 50%"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pool_system_health
      below: 50
      for:
        minutes: 5
  action:
    - service: violet_pool_controller.get_connection_status
      target:
        device_id: YOUR_DEVICE_ID
      response_variable: status_data
    - service: notify.mobile_app_your_phone
      data:
        title: "🏥 Pool Controller: Low System Health"
        message: |
          System health: {{ states('sensor.pool_system_health') }}%
          Consecutive failures: {{ status_data.devices[0].consecutive_failures }}
          Check the integration logs for more details.
```

---

## Diagnostic Automations

### 8. Export Diagnostic Logs Daily

```yaml
- alias: "Pool: Daily Diagnostic Export"
  id: "pool_daily_diag"
  description: "Export diagnostic logs every day at midnight"
  trigger:
    - platform: time
      at: "00:00:00"
  action:
    - service: violet_pool_controller.export_diagnostic_logs
      target:
        device_id: YOUR_DEVICE_ID
      data:
        lines: 500
        include_config: true
        include_history: true
        include_states: true
        include_raw_data: true
        save_to_file: true
      response_variable: diag_data
    - service: notify.mobile_app_your_phone
      data:
        title: "📊 Pool Diagnostic Log Exported"
        message: "Daily diagnostic logs saved to: {{ diag_data.filename }}"
```

### 9. Export Logs on Errors

```yaml
- alias: "Pool: Export Logs on Error"
  id: "pool_export_on_error"
  description: "Export logs when controller goes offline"
  trigger:
    - platform: state
      entity_id: binary_sensor.pool_controller_status
      to: "off"
  action:
    - delay:
        minutes: 2  # Wait for potential quick recovery
    - condition: state
      entity_id: binary_sensor.pool_controller_status
      state: "off"
    - service: violet_pool_controller.export_diagnostic_logs
      target:
        device_id: YOUR_DEVICE_ID
      data:
        lines: 1000
        save_to_file: true
```

---

## Alert Notifications

### 10. Critical Error Notification

```yaml
- alias: "Pool: Critical Error Alert"
  id: "pool_critical_alert"
  description: "Send critical alerts for severe issues"
  trigger:
    - platform: template
      value_template: >
        {{ state_attr('sensor.pool_last_error', 'severity') == 'high' }}
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "🚨 POOL CONTROLLER: CRITICAL ERROR"
        message: |
          Error: {{ state_attr('sensor.pool_last_error', 'message') }}
          Type: {{ state_attr('sensor.pool_last_error', 'type') }}
          Time: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
        data:
          push:
            sound: alarm
            badge: 5
            priority: high
```

### 11. Scheduled Health Check Summary

```yaml
- alias: "Pool: Weekly Health Summary"
  id: "pool_weekly_summary"
  description: "Send weekly health check summary"
  trigger:
    - platform: time
      at: "09:00:00"
    - condition: time
      weekday:
        - mon
  action:
    - service: violet_pool_controller.get_connection_status
      target:
        device_id: YOUR_DEVICE_ID
      response_variable: status
    - service: violet_pool_controller.get_error_summary
      target:
        device_id: YOUR_DEVICE_ID
      response_variable: errors
    - service: notify.mobile_app_your_phone
      data:
        title: "🌊 Pool Controller: Weekly Health Summary"
        message: |
          System Health: {{ states('sensor.pool_system_health') }}%
          Connection Latency: {{ states('sensor.pool_connection_latency') }}ms
          Total Errors (week): {{ errors.devices[0].error_summary.total_errors }}
          Controller Status: {{ states('binary_sensor.pool_controller_status') }}
          Last Update: {{ status.devices[0].last_update | timestamp_custom('%Y-%m-%d %H:%M:%S', true) }}
```

---

## Helper Templates

### Template Sensors for Monitoring

```yaml
template:
  - sensor:
      - name: "Pool Consecutive Errors"
        state: "{{ state_attr('binary_sensor.pool_controller_status', 'consecutive_failures') | int }}"
        unit_of_measurement: "errors"

      - name: "Pool Auth Errors"
        state: "{{ state_attr('sensor.pool_error_summary', 'auth_errors') | int }}"
        unit_of_measurement: "errors"

      - name: "Pool Offline Duration"
        state: "{{ state_attr('sensor.pool_error_summary', 'offline_duration_seconds') | int }}"
        unit_of_measurement: "s"

      - name: "Pool Last Error Type"
        state: "{{ state_attr('sensor.pool_last_error', 'type') }}"

      - name: "Pool Last Error Severity"
        state: "{{ state_attr('sensor.pool_last_error', 'severity') | title }}"
```

---

## Integration with Other Systems

### 12. Pause Automations on Offline

```yaml
- alias: "Pool: Pause Automations When Offline"
  id: "pool_pause_automations"
  description: "Pause pool-related automations when controller is offline"
  trigger:
    - platform: state
      entity_id: binary_sensor.pool_controller_status
      to: "off"
  action:
    - service: automation.turn_off
      target:
        entity_id:
          - automation.pool_ph_control
          - automation.pool_chlorine_dosing
          - automation.pool_solar_heating
    - service: notify.mobile_app_your_phone
      data:
        title: "⏸️ Pool Automations Paused"
        message: "Controller is offline. Pool control automations have been paused."

- alias: "Pool: Resume Automations When Online"
  id: "pool_resume_automations"
  description: "Resume pool-related automations when controller comes back online"
  trigger:
    - platform: state
      entity_id: binary_sensor.pool_controller_status
      to: "on"
      for:
        minutes: 5
  action:
    - service: automation.turn_on
      target:
        entity_id:
          - automation.pool_ph_control
          - automation.pool_chlorine_dosing
          - automation.pool_solar_heating
    - service: notify.mobile_app_your_phone
      data:
        title: "▶️ Pool Automations Resumed"
        message: "Controller is back online. Pool control automations have been resumed."
```

---

## Advanced Troubleshooting

### 13. Automatic Diagnostic Collection

```yaml
- alias: "Pool: Auto-Collect Diagnostics on Issues"
  id: "pool_auto_diag"
  description: "Automatically collect diagnostic information when issues are detected"
  trigger:
    - platform: template
      value_template: >
        {{ states('sensor.pool_consecutive_errors') | int(0) > 5 }}
  action:
    - parallel:
        - service: violet_pool_controller.test_connection
          target:
            device_id: YOUR_DEVICE_ID
          response_variable: conn_test
        - service: violet_pool_controller.get_connection_status
          target:
            device_id: YOUR_DEVICE_ID
          response_variable: conn_status
        - service: violet_pool_controller.get_error_summary
          target:
            device_id: YOUR_DEVICE_ID
          data:
            include_history: true
          response_variable: error_summary
    - service: notify.mobile_app_your_phone
      data:
        title: "🔍 Pool: Diagnostic Data Collected"
        message: |
          Connection Test: {{ 'PASS' if conn_test.tests[0].success else 'FAIL' }}
          Latency: {{ conn_status.devices[0].connection_latency_ms }}ms
          System Health: {{ conn_status.devices[0].system_health }}%
          Total Errors: {{ error_summary.devices[0].error_summary.total_errors }}
          Recovery Action: {{ error_summary.devices[0].recovery_suggestion }}
```

---

## Notes

1. **Replace `YOUR_DEVICE_ID`** with your actual device ID from Home Assistant
2. **Replace `mobile_app_your_phone`** with your actual notification service
3. **Adjust thresholds** (latency, error counts, etc.) to match your environment
4. **Test automations** in Developer Tools before activating them
5. **Enable debug logging** for detailed troubleshooting:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.violet_pool_controller: debug
   ```

For more troubleshooting information, see the main [README.md](../README.md) and [TROUBLESHOOTING.md](../README.md#troubleshooting).
