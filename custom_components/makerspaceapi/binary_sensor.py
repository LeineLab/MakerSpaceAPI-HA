"""Binary sensor platform: rental items (is_rented)."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MakerSpaceCoordinator
from .entity import MakerSpaceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MakerSpaceCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_items: set[str] = set()

    @callback
    def _add_new_entities() -> None:
        new: list[BinarySensorEntity] = []

        for item in coordinator.data.get("catalog", []):
            tid: str = item["uhf_tid"]
            if tid not in known_items:
                known_items.add(tid)
                new.append(RentalItemSensor(coordinator, entry, tid))

        if new:
            async_add_entities(new)

    entry.async_on_unload(coordinator.async_add_listener(_add_new_entities))
    _add_new_entities()


class RentalItemSensor(MakerSpaceEntity, BinarySensorEntity):
    """Binary sensor: ON (present) when the item is available, OFF (away) when rented out."""

    _attr_device_class = BinarySensorDeviceClass.PRESENCE

    def __init__(
        self, coordinator: MakerSpaceCoordinator, entry: ConfigEntry, uhf_tid: str
    ) -> None:
        super().__init__(coordinator, entry)
        self._uhf_tid = uhf_tid
        self._attr_unique_id = f"{entry.entry_id}_rental_{uhf_tid}"

    def _item(self) -> dict | None:
        for i in self.coordinator.data.get("catalog", []):
            if i["uhf_tid"] == self._uhf_tid:
                return i
        return None

    @property
    def name(self) -> str:
        item = self._item()
        return item["name"] if item else f"Item {self._uhf_tid}"

    @property
    def icon(self) -> str:
        return "mdi:tag" if self.is_on else "mdi:tag-remove"

    @property
    def is_on(self) -> bool | None:
        item = self._item()
        return (not item["is_rented"]) if item else None

    @property
    def available(self) -> bool:
        return super().available and self._item() is not None

    @property
    def extra_state_attributes(self) -> dict:
        item = self._item()
        return {"uhf_tid": self._uhf_tid, "name": item["name"] if item else None}
