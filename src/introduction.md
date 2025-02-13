# Introduction

Welcome to the documentation for the **Violet Pool Controller** integration for Home Assistant! This custom component allows you to seamlessly integrate your Violet Pool Controller into your Home Assistant ecosystem, giving you control and monitoring of your pool equipment directly within Home Assistant.

## What is the Violet Pool Controller?

The Violet Pool Controller, by [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart), is a smart, all-in-one pool control system.  It's designed to manage various aspects of your pool, including filtration, heating, lighting, backwashing, and more.  The controller provides a web interface and a JSON API, which this integration utilizes to connect to Home Assistant.

## What Does This Integration Do?

This integration leverages the Violet Pool Controller's API to:

*   **Monitor Pool Status:**  Track key metrics like water temperature, filter pressure, pump speed, pH levels, ORP levels, and more, all within Home Assistant.  These are exposed as `sensor` entities.
*   **Control Pool Equipment:**  Control your pool pump, lights, and other connected devices directly from Home Assistant.  This is achieved through `switch` entities.  You can turn devices on/off manually, or switch them to "Auto" mode, allowing the Violet controller's internal logic to take over.
*   **Automate Pool Operations:**  Create Home Assistant automations based on sensor values or time schedules.  For example, you can automatically run the pump for a specific duration, turn on the lights at sunset, or adjust chemical dosing based on sensor readings.
*    **Custom Services:** Includes custom Home Assistant services like `switch.turn_on` (with duration), `switch.turn_off`, and `switch.turn_auto` for use in automations.

## Key Features

*   **Local Polling:**  The integration communicates directly with your Violet Pool Controller over your local network.  No cloud connection is required, ensuring fast response times and enhanced privacy.
*   **Automatic Updates:**  The integration uses a `DataUpdateCoordinator` to efficiently fetch data from the controller at a configurable interval.
*   **Comprehensive Sensors:**  Provides a wide range of sensors to monitor various aspects of your pool's operation.
*   **Controllable Switches:**  Allows you to control key pool equipment directly from Home Assistant.
*   **Easy Configuration:**  Configuration is done entirely through the Home Assistant UI, with no need to edit YAML files.
*   **Robust Error Handling:**  Includes error handling and retry mechanisms to ensure reliable operation.
*   **Open Source:**  The integration is open-source and available on [GitHub](https://github.com/Xerolux/violet-hass).

## Prerequisites

Before you begin, make sure you have the following:

*   A functioning Violet Pool Controller installed and connected to your local network.
*   Home Assistant instance (version 2023.9.0 or later recommended).
*   The IP address or hostname of your Violet Pool Controller.
*   (Optional) Username and password for your Violet Pool Controller (if authentication is enabled).

## Getting Started

The next sections of this documentation will guide you through the installation and configuration process.  Let's get started!
