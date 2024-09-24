STEP_USER_TITLE = "Configure Violet Device"
STEP_USER_DESCRIPTION = (
    "Please enter the API URL, credentials for device control, and choose if SSL should be used. "
    "Ensure the API URL is correct and reachable."
)

# Configuration form field labels
FIELD_API_URL = "API URL (e.g., http://192.168.x.x/getReadings?ALL)"
FIELD_USERNAME = "Username for device control"
FIELD_PASSWORD = "Password for device control"
FIELD_POLLING_INTERVAL = "Polling Interval (seconds)"
FIELD_USE_SSL = "Use SSL (Check for HTTPS)"

# Error messages
ERROR_CANNOT_CONNECT = (
    "Cannot connect to the device. Please check the API URL or SSL settings."
)
ERROR_INVALID_URL = "The API URL format is invalid. Please check and try again."
ERROR_SSL = "SSL connection failed. Ensure SSL is enabled on the device or disable SSL."
ERROR_TIMEOUT = "The connection to the device timed out. Please try again later."
ERROR_UNKNOWN = (
    "An unknown error occurred. Please try again or check the logs for more details."
)
{
  "config": {
    "step": {
      "user": {
        "data": {
          "api_url": "API URL (e.g., http://192.168.x.x/getReadings?ALL)",
          "username": "Username for device control",
          "password": "Password for device control",
          "polling_interval": "Polling Interval (seconds)",
          "use_ssl": "Use SSL (Check for HTTPS)"
        },
        "title": "Configure Violet Device",
        "description": "Please enter the API URL, credentials for device control, and choose if SSL should be used. Ensure the API URL is correct and reachable."
      }
    },
    "error": {
      "cannot_connect": "Cannot connect to the device. Please check the API URL or SSL settings.",
      "invalid_url": "The API URL format is invalid. Please check and try again.",
      "ssl_error": "SSL connection failed. Ensure SSL is enabled on the device or disable SSL.",
      "timeout": "The connection to the device timed out. Please try again later.",
      "unknown": "An unknown error occurred. Please try again or check the logs for more details."
    }
  }
}
