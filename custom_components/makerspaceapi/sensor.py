"""Sensor platform: products (stock) and booking targets (balance)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
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

    known_products: set[str] = set()
    known_targets: set[str] = set()

    @callback
    def _add_new_entities() -> None:
        new: list[SensorEntity] = []

        for product in coordinator.data.get("products", []):
            ean: str = product["ean"]
            if ean not in known_products:
                known_products.add(ean)
                new.append(ProductSensor(coordinator, entry, ean))

        for target in coordinator.data.get("targets", []):
            slug: str = target["slug"]
            if slug not in known_targets:
                known_targets.add(slug)
                new.append(BookingTargetSensor(coordinator, entry, slug))

        if new:
            async_add_entities(new)

    entry.async_on_unload(coordinator.async_add_listener(_add_new_entities))
    _add_new_entities()


# ---------------------------------------------------------------------------
# Product sensor — state: current stock count
# ---------------------------------------------------------------------------

class ProductSensor(MakerSpaceEntity, SensorEntity):
    """Stock level for a single product."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "items"

    def __init__(
        self, coordinator: MakerSpaceCoordinator, entry: ConfigEntry, ean: str
    ) -> None:
        super().__init__(coordinator, entry)
        self._ean = ean
        self._attr_unique_id = f"{entry.entry_id}_product_{ean}"

    def _product(self) -> dict | None:
        for p in self.coordinator.data.get("products", []):
            if p["ean"] == self._ean:
                return p
        return None

    @property
    def name(self) -> str:
        p = self._product()
        return p["name"] if p else f"Product {self._ean}"

    @property
    def icon(self) -> str:
        p = self._product()
        if not p:
            return "mdi:help"
        if p["category"].lower() in ("drinks", "drink", "getränke", "getränk", "beer", "bier"):
            return "mdi:cup" if p["stock"] > 0 else "mdi:cup-off"
        if p["category"].lower() in ("snacks", "snack", "food", "essen"):
            return "mdi:peanut" if p["stock"] > 0 else "mdi:peanut-off"
        if p["category"].lower() in ("sweets", "candy", "süßigkeiten"):
            return "mdi:candy" if p["stock"] > 0 else "mdi:candy-off"
        return "mdi:package-variant" if p["stock"] > 0 else "mdi:package-variant-remove"
    
    @property
    def native_value(self) -> int | None:
        p = self._product()
        return p["stock"] if p else None

    @property
    def available(self) -> bool:
        return super().available and self._product() is not None

    @property
    def extra_state_attributes(self) -> dict:
        p = self._product()
        if not p:
            return {}
        return {
            "ean": p["ean"],
            "price": float(p["price"]),
            "category": p["category"],
            "active": p["active"],
        }


# ---------------------------------------------------------------------------
# Booking target sensor — state: current balance in EUR
# ---------------------------------------------------------------------------

class BookingTargetSensor(MakerSpaceEntity, SensorEntity):
    """Current balance of a booking target."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CURRENCY_EURO
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:cash"

    def __init__(
        self, coordinator: MakerSpaceCoordinator, entry: ConfigEntry, slug: str
    ) -> None:
        super().__init__(coordinator, entry)
        self._slug = slug
        self._attr_unique_id = f"{entry.entry_id}_target_{slug}"

    def _target(self) -> dict | None:
        for t in self.coordinator.data.get("targets", []):
            if t["slug"] == self._slug:
                return t
        return None

    @property
    def name(self) -> str:
        t = self._target()
        return t["name"] if t else f"Target {self._slug}"

    @property
    def icon(self) -> str:
        t = self._target()
        if not t:
            return "mdi:cash-sync"
        return "mdi:cash" if t["balance"] > 0 else "mdi:cash-off"

    @property
    def native_value(self) -> float | None:
        t = self._target()
        return float(t["balance"]) if t else None

    @property
    def available(self) -> bool:
        return super().available and self._target() is not None

    @property
    def extra_state_attributes(self) -> dict:
        t = self._target()
        if not t:
            return {}
        return {"slug": t["slug"], "id": t["id"]}
