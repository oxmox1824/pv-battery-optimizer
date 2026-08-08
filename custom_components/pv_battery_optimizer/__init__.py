from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PVBatteryOptimizerCoordinator

PLATFORMS = [
    "sensor",
]


def _flatten_config(data: dict) -> dict:
    """
    Sections im Config Flow liefern verschachtelte Dicts.
    Diese Funktion flacht eine Ebene tief ab, sodass der Coordinator
    alle Schlüssel direkt ansprechen kann.
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result.update(value)
        else:
            result[key] = value
    return result


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Richte den PV Battery Optimizer ein."""
    config = _flatten_config({
        **entry.data,
        **entry.options,
    })

    coordinator = PVBatteryOptimizerCoordinator(
        hass,
        config,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(
        DOMAIN,
        {},
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(_async_update_listener)
    )

    return True


async def _async_update_listener(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Lade die Integration neu wenn Optionen geändert wurden."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Entferne den PV Battery Optimizer sauber."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(
            entry.entry_id,
            None,
        )

    return unload_ok