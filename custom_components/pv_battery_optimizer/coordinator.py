from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_LANGUAGE,
    CONF_POWER_LIMIT,
    CONF_WRITE_TO_SENSOR,
    DEFAULT_LANGUAGE,
    DEFAULT_WRITE_TO_SENSOR,
)
from .energy_model import EnergyModel
from .language import text
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
        """Lese Sensorwerte, berechne Optimierungsdaten und schreibe ggf. auf den Wechselrichter."""
        _LOGGER.debug("Coordinator Update")

        try:
            energy_data = self.reader.read()
            model = EnergyModel(energy_data)
            recommendation = model.recommendation()
            language = self.config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)

            result = {
                "soc": energy_data.soc,
                "pv_power": energy_data.pv_power,
                "pv_remaining": energy_data.pv_remaining,
                "house_power": energy_data.house_power,
                "price": energy_data.price if energy_data.price is not None else 0.0,
                "max_power": energy_data.max_power,
                "missing_energy": round(model.missing_energy(), 2),
                "pv_surplus": round(model.pv_surplus(), 0),
                "possible_soc": round(model.possible_soc_today(), 1),
                "can_reach_full": model.can_reach_full(),
                "should_charge_from_grid": recommendation["should_charge_from_grid"],
                "recommended_charge_power": recommendation["recommended_power"],
                "recommended_charge_power_exact": recommendation.get(
                    "recommended_power_exact", recommendation["recommended_power"]
                ),
                "negative_price_hours_today": (
                    self.reader.negative_price_hours("today")
                ),
                "negative_price_hours_tomorrow": (
                    self.reader.negative_price_hours("tomorrow")
                ),
                "recommendation": text(
                    language, f"action_{recommendation['action']}"
                ),
                "charge_source": text(
                    language, f"source_{recommendation['source']}"
                ),
                "recommendation_reason": text(language, recommendation["reason"]),
            }

        except Exception as err:
            _LOGGER.exception("Fehler beim Aktualisieren des PV Battery Optimizers")
            raise UpdateFailed(
                f"Sensorwerte konnten nicht verarbeitet werden: {err}"
            ) from err

        _LOGGER.debug(
            "OPTIMIZER DATA: SOC=%s PV=%s HOUSE=%s PRICE=%s POWER=%s REASON=%s",
            energy_data.soc,
            energy_data.pv_power,
            energy_data.house_power,
            energy_data.price,
            result["recommended_charge_power"],
            result["recommendation_reason"],
        )

        # Empfohlene Ladeleistung direkt auf den Wechselrichter schreiben
        write_enabled = self.config.get(CONF_WRITE_TO_SENSOR, DEFAULT_WRITE_TO_SENSOR)
        if write_enabled:
            power_entity = self.config.get(CONF_POWER_LIMIT)
            power_value = result["recommended_charge_power"]

            if power_entity and power_value is not None:
                # Wechselrichter akzeptiert keinen Wert unter seinem min-Attribut.
                # Bei 0 W (kein Entladeschutz nötig) den kleinsten erlaubten Wert nutzen.
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
                    _LOGGER.debug(
                        "Ladeleistung gesetzt: %s W → %s",
                        power_value,
                        power_entity,
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "Fehler beim Schreiben der Ladeleistung auf %s: %s",
                        power_entity,
                        err,
                    )

        return result
