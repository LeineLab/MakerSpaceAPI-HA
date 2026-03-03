"""Config flow for MakerSpaceAPI integration."""
from __future__ import annotations

from urllib.parse import urlparse

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_TOKEN, CONF_URL, DOMAIN

_STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Required(CONF_TOKEN): str,
    }
)


class MakerSpaceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")

            # Prevent duplicate entries for the same base URL
            await self.async_set_unique_id(url.lower())
            self._abort_if_unique_id_configured()

            # Verify the API is reachable
            session = async_get_clientsession(self.hass)
            try:
                async with session.get(
                    f"{url}/api/v1/products",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    resp.raise_for_status()
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                title = urlparse(url).netloc or url
                return self.async_create_entry(
                    title=title,
                    data={CONF_URL: url, CONF_TOKEN: user_input[CONF_TOKEN]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_STEP_USER_SCHEMA,
            errors=errors,
        )
