"""Shared base entity for MakerSpaceAPI entities."""
from __future__ import annotations

from urllib.parse import urlparse

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_URL, DOMAIN
from .coordinator import MakerSpaceCoordinator


class MakerSpaceEntity(CoordinatorEntity[MakerSpaceCoordinator]):
    """Base entity that pins all sensors to the same HA device per config entry."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MakerSpaceCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        url = self._entry.data[CONF_URL]
        host = urlparse(url).netloc or url
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"MakerSpaceAPI ({host})",
            manufacturer="LeineLab e.V.",
            model="MakerSpaceAPI",
            configuration_url=url,
        )
