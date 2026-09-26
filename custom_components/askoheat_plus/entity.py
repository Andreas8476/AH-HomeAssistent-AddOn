"""Basis-Entity für die ASKOHEAT+-Integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AskoheatDataUpdateCoordinator


class AskoheatEntity(CoordinatorEntity[AskoheatDataUpdateCoordinator]):
    """Gemeinsame Basis für alle ASKOHEAT+-Entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        device_id = coordinator.device_id or coordinator.config_entry.entry_id
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info
