{
  "config": {
    "step": {
      "user": {
        "data": {
          "api_url": "API URL (e.g., http://192.168.x.x/getReadings?ALL)",
          "polling_interval": "Polling Interval (seconds)",
          "use_ssl": "Use SSL (Check for HTTPS)"
        },
        "title": "Configure Violet Device",
        "description": "Please enter the API URL and choose if SSL should be used. Ensure the API URL is correct and reachable."
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
