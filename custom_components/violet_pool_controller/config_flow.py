import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_API_URL, CONF_POLLING_INTERVAL

@callback
def configured_instances(hass):
    """Return a set of configured instances."""
    return set(entry.data[CONF_API_URL] for entry in hass.config_entries.async_entries(DOMAIN))

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Device."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Save the user input
            return self.async_create_entry(title="Violet Device", data=user_input)

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_URL, default="http://192.168.178.55/getReadings?ALL"): str,
                vol.Optional(CONF_POLLING_INTERVAL, default=10): int,
            })
        )
