from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_POWER_LIMIT,
    CONF_WRITE_TO_SENSOR,
    DEFAULT_WRITE_TO_SENSOR,
    SENSOR_CAN_REACH_FULL,
    SENSOR_CHARGE_SOURCE,
    SENSOR_HOUSE_POWER,
    SENSOR_MAX_POWER,
    SENSOR_MISSING_ENERGY,
    SENSOR_NEG_PRICE_HOURS_TODAY,
    SENSOR_NEG_PRICE_HOURS_TOMORROW,
    SENSOR_POSSIBLE_SOC,
    SENSOR_PRICE,
    SENSOR_PV_POWER,
    SENSOR_PV_REMAINING,
    SENSOR_PV_SURPLUS,
    SENSOR_RECOMMENDATION,
    SENSOR_RECOMMENDATION_REASON,
    SENSOR_RECOMMENDED_CHARGE_POWER,
    SENSOR_RECOMMENDED_CHARGE_POWER_EXACT,
    SENSOR_SOC,
)
from .energy_model import EnergyModel
from .sensor_reader import SensorReader

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=60)


class PVBatteryOptimizerCoordinator(DataUpdateCoordinator):
    """Koordiniert das Einlesen und Berechnen der PV-Batteriedaten."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self.hass = hass
        self.config = config
        self.reader = SensorReader(hass, config)

        super().__init__(
            hass,
            _LOGGER,
            name="PV Battery Optimizer",
            update_interval=UPDATE_INTERVAL,
            always_update=True,
        )

    async def _async_update_data(self) -> dict:
        """Lese Sensorwerte und berechne Optimierungsdaten."""
        _LOGGER.debug("Coordinator Update")

        try:
            energy_data = self.reader.read()
            model = EnergyModel(energy_data)
            recommendation = model.recommendation()

            result = {
                SENSOR_SOC: energy_data.soc,
                SENSOR_PV_POWER: energy_data.pv_power,
                SENSOR_PV_REMAINING: energy_data.pv_remaining,
                SENSOR_HOUSE_POWER: energy_data.house_power,
                SENSOR_PRICE: energy_data.price if energy_data.price is not None else 0.0,
                SENSOR_MAX_POWER: energy_data.max_power,
                SENSOR_MISSING_ENERGY: round(model.missing_energy(), 2),
                SENSOR_PV_SURPLUS: round(model.pv_surplus(), 0),
                SENSOR_POSSIBLE_SOC: round(model.possible_soc_today(), 1),
                SENSOR_CAN_REACH_FULL: model.can_reach_full(),
                SENSOR_RECOMMENDATION: recommendation["action"],
                SENSOR_CHARGE_SOURCE: recommendation["source"],
                SENSOR_RECOMMENDATION_REASON: recommendation["reason"],
                SENSOR_RECOMMENDED_CHARGE_POWER: recommendation["recommended_power"],
                SENSOR_RECOMMENDED_CHARGE_POWER_EXACT: recommendation.get(
                    "recommended_power_exact", recommendation["recommended_power"]
                ),
                SENSOR_NEG_PRICE_HOURS_TODAY: (
                    self.reader.negative_price_hours("today")
                ),
                SENSOR_NEG_PRICE_HOURS_TOMORROW: (
                    self.reader.negative_price_hours("tomorrow")
                ),
            }

        except Exception as err:
            _LOGGER.exception("Fehler beim Aktualisieren des PV Battery Optimizers")
            raise UpdateFailed(
                f"Sensorwerte konnten nicht verarbeitet werden: {err}"
            ) from err

        await self._async_write_power_to_device(result[SENSOR_RECOMMENDED_CHARGE_POWER])

        return result

    async def _async_write_power_to_device(self, power_value: float) -> None:
        """Schreibt die empfohlene Ladeleistung auf den Wechselrichter, falls aktiviert."""
        write_enabled = self.config.get(CONF_WRITE_TO_SENSOR, DEFAULT_WRITE_TO_SENSOR)
        if not write_enabled:
            return

        power_entity = self.config.get(CONF_POWER_LIMIT)
        if not power_entity or power_value is None:
            return

        state = self.hass.states.get(power_entity)
        if state is not None and power_value == 0:
            try:
                min_val = float(state.attributes.get("min", 0))
                power_value = min_val
            except (ValueError, TypeError):
                pass

        try:
            await self.hass.services.async_call(
                "number",
                "set_value",
                {
                    "entity_id": power_entity,
                    "value": power_value,
                },
                blocking=False,
            )
        except Exception as err:
            _LOGGER.warning(
                "Fehler beim Schreiben der Ladeleistung auf %s: %s",
                power_entity,
                err,
            )
