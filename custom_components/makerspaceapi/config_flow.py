"""Config flow for MakerSpaceAPI integration."""
from __future__ import annotations

from urllib.parse import urlparse

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Optional(CONF_TOKEN, default=""): str,
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MakerSpaceOptionsFlow:
        return MakerSpaceOptionsFlow()


class MakerSpaceOptionsFlow(config_entries.OptionsFlow):
    """Let the user change the poll interval after setup."""

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
