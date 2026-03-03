"""DataUpdateCoordinator for MakerSpaceAPI."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

_TIMEOUT = aiohttp.ClientTimeout(total=10)


class MakerSpaceCoordinator(DataUpdateCoordinator[dict]):
    """Fetches products (always), booking targets and rental catalog (when token provided)."""

    def __init__(self, hass: HomeAssistant, base_url: str, token: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)

        # Products are always fetched (public endpoint).
        try:
            async with session.get(
                f"{self.base_url}/api/v1/products", timeout=_TIMEOUT
            ) as resp:
                resp.raise_for_status()
                products: list = await resp.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise UpdateFailed(f"Cannot reach MakerSpaceAPI at {self.base_url}: {exc}") from exc

        # Booking targets and rental catalog require a device token.
        targets: list = []
        catalog: list = []
        if self.token:
            auth_headers = {"Authorization": f"Bearer {self.token}"}
            try:
                async with session.get(
                    f"{self.base_url}/api/v1/bankomat/targets",
                    headers=auth_headers,
                    timeout=_TIMEOUT,
                ) as resp:
                    resp.raise_for_status()
                    targets = await resp.json()
            except Exception as exc:  # noqa: BLE001
                _LOGGER.warning("Could not fetch booking targets from %s: %s", self.base_url, exc)

            try:
                async with session.get(
                    f"{self.base_url}/api/v1/rentals/catalog",
                    headers=auth_headers,
                    timeout=_TIMEOUT,
                ) as resp:
                    resp.raise_for_status()
                    catalog = await resp.json()
            except Exception as exc:  # noqa: BLE001
                _LOGGER.warning("Could not fetch rental catalog from %s: %s", self.base_url, exc)

        return {"products": products, "targets": targets, "catalog": catalog}
