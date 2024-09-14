import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

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
            # Check if device already exists
            await self.async_set_unique_id(user_input[CONF_API_URL])
            self._abort_if_unique_id_configured()

            # Save the user input
            return self.async_create_entry(title="Violet Device", data=user_input)

        # Reminder to enter the correct Violet Pool Controller IP
        reminder_text = (
            "Please enter the IP of your Violet Pool Controller "
            "(e.g., http://192.168.178.55/getReadings?ALL). "
            "Note: Most sensors in Violet can only be polled every 10 seconds. "
            "Reducing the interval will increase the load on Violet and your network without providing more accurate data."
        )

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_URL, default="http://192.168.178.55/getReadings?ALL"): vol.Url(),
                vol.Optional(CONF_POLLING_INTERVAL, default=10): vol.All(vol.Coerce(int), vol.Range(min=10)),
            }),
            description_placeholders={"ip_reminder": reminder_text}
        )
