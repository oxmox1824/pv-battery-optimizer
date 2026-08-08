import logging
from dataclasses import dataclass
from datetime import datetime

from homeassistant.core import HomeAssistant

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_BATTERY_SOC,
    CONF_CHARGE_EFFICIENCY,
    CONF_DISCHARGE_BUFFER_POWER,
    CONF_DISCHARGE_EFFICIENCY,
    CONF_EVENING_TARGET_HOURS,
    CONF_EVENING_TARGET_SOC,
    CONF_HOUSE_POWER,
    CONF_MIN_DISCHARGE_POWER,
    CONF_MIN_SOC,
    CONF_NORDPOOL,
    CONF_POWER_LIMIT,
    CONF_PV_DAY_FACTOR,
    CONF_PV_POWER,
    CONF_PV_REMAINING,
    CONF_STRATEGY,
    CONF_TARGET_SOC,
    DEFAULT_DISCHARGE_BUFFER_POWER,
    DEFAULT_EVENING_TARGET_HOURS,
    DEFAULT_EVENING_TARGET_SOC,
    DEFAULT_MAX_POWER_FALLBACK,
    DEFAULT_MIN_DISCHARGE_POWER,
    DEFAULT_PV_DAY_FACTOR,
    DEFAULT_STRATEGY,
)


_LOGGER = logging.getLogger(__name__)


@dataclass
class EnergyData:
    soc: float
    pv_power: float
    pv_remaining: float
    house_power: float
    price: float | None
    max_power: float
    battery_capacity: float
    min_soc: float
    target_soc: float
    charge_efficiency: float
    discharge_efficiency: float
    strategy: str
    min_discharge_power: float
    evening_target_soc: float
    evening_target_hours: float
    pv_day_factor: float
    discharge_buffer_power: float
    sunset_time: datetime | None


class SensorReader:

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict,
    ) -> None:
        self.hass = hass
        self.config = config

    def get_value(
        self,
        entity_id: str | None,
        default: float = 0.0,
    ) -> float:
        if not entity_id:
            _LOGGER.warning("Keine Entity konfiguriert")
            return default

        state = self.hass.states.get(entity_id)

        if state is None:
            _LOGGER.debug("Sensor noch nicht verfügbar: %s", entity_id)
            return default

        # unknown/unavailable sind normale Startzustände
        if state.state in ("unknown", "unavailable"):
            _LOGGER.debug(
                "Sensor %s meldet %s – Fallback auf %.1f",
                entity_id, state.state, default,
            )
            return default

        try:
            return float(state.state)
        except (ValueError, TypeError):
            _LOGGER.warning(
                "Ungültiger Wert: %s = %s", entity_id, state.state
            )
            return default

    def _read_sunset(self) -> datetime | None:
        """Liest den nächsten Sonnenuntergang aus sun.sun."""
        sun_state = self.hass.states.get("sun.sun")
        if sun_state is None:
            _LOGGER.debug("sun.sun noch nicht verfügbar")
            return None

        next_setting = sun_state.attributes.get("next_setting")
        if not next_setting:
            return None

        try:
            # HA liefert einen ISO-String mit Zeitzone
            if isinstance(next_setting, str):
                dt = datetime.fromisoformat(
                    next_setting.replace("Z", "+00:00")
                )
            else:
                dt = next_setting

            # In naive local time umwandeln für einfache Differenzberechnung.
            # astimezone() konvertiert zuerst in die lokale Zeitzone,
            # erst dann wird tzinfo entfernt — sonst würde UTC-Zeit als
            # Lokalzeit interpretiert und die Differenz wäre um den
            # UTC-Offset falsch (z.B. -2h in Deutschland).
            return dt.astimezone().replace(tzinfo=None)
        except (ValueError, TypeError):
            _LOGGER.warning("Ungültiger Sonnenuntergang-Wert: %s", next_setting)
            return None

    def negative_price_hours(self, day_key: str) -> float:
        """
        Berechnet die Stunden mit negativen Boersenpreisen fuer 'today'
        oder 'tomorrow' aus den Attributen des Nordpool-Sensors.
        Jeder Eintrag repraesentiert 15 Minuten (1/4 Stunde).
        """
        entity_id = self.config.get(CONF_NORDPOOL)
        if not entity_id:
            return 0.0

        state = self.hass.states.get(entity_id)
        if state is None:
            return 0.0

        prices = state.attributes.get(day_key)
        if not prices or not isinstance(prices, list):
            return 0.0

        negative_slots = sum(1 for p in prices if isinstance(p, (int, float)) and p < 0)
        return round(negative_slots * 0.25, 2)

    def _read_price(self) -> float | None:
        """
        Liest den aktuellen Strompreis. Gibt None zurück wenn der Sensor
        unavailable oder unknown ist (z.B. während des täglichen Updates),
        damit 0.0 ct/kWh von einem fehlenden Wert unterschieden wird.
        """
        entity_id = self.config.get(CONF_NORDPOOL)
        if not entity_id:
            return None

        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable"):
            _LOGGER.debug("Nordpool-Sensor nicht verfügbar: %s", entity_id)
            return None

        try:
            return float(state.state)
        except (ValueError, TypeError):
            _LOGGER.warning("Ungültiger Preiswert: %s = %s", entity_id, state.state)
            return None

    def _read_max_power(self) -> float:
        """
        Liest die maximale Ladeleistung aus dem max-Attribut der number-Entität.
        Damit wird der Kreislauf vermieden, bei dem die Integration ihren eigenen
        zuvor geschriebenen Wert als Obergrenze liest.
        Fallback: DEFAULT_MAX_POWER_FALLBACK wenn Entität nicht verfügbar.
        """
        entity_id = self.config.get(CONF_POWER_LIMIT)
        if not entity_id:
            return DEFAULT_MAX_POWER_FALLBACK

        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable"):
            return DEFAULT_MAX_POWER_FALLBACK

        # max-Attribut bevorzugen (Hardware-Grenze, unveränderlich)
        max_attr = state.attributes.get("max")
        if max_attr is not None:
            try:
                return float(max_attr)
            except (ValueError, TypeError):
                pass

        # Fallback auf aktuellen Zustand wenn kein max-Attribut vorhanden
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return DEFAULT_MAX_POWER_FALLBACK

    def read(self) -> EnergyData:
        soc = self.get_value(self.config.get(CONF_BATTERY_SOC))
        pv_power = self.get_value(self.config.get(CONF_PV_POWER))
        house_power = self.get_value(self.config.get(CONF_HOUSE_POWER))
        max_power = self._read_max_power()

        # Preis separat lesen: None wenn Sensor unavailable/unknown,
        # damit 0.0-Preis von fehlendem Preis unterschieden werden kann
        price = self._read_price()

        remaining_sensors = self.config.get(CONF_PV_REMAINING, [])
        if isinstance(remaining_sensors, str):
            remaining_sensors = [remaining_sensors]

        pv_remaining = 0.0
        for sensor in remaining_sensors:
            value = self.get_value(sensor)
            _LOGGER.debug("PV Remaining %s = %.3f kWh", sensor, value)
            pv_remaining += value

        battery_capacity = float(
            self.config.get(CONF_BATTERY_CAPACITY, 10.0)
        )
        min_soc = float(self.config.get(CONF_MIN_SOC, 10.0))
        target_soc = float(self.config.get(CONF_TARGET_SOC, 100.0))
        charge_efficiency = float(
            self.config.get(CONF_CHARGE_EFFICIENCY, 95.0)
        )
        discharge_efficiency = float(
            self.config.get(CONF_DISCHARGE_EFFICIENCY, 95.0)
        )
        strategy = str(self.config.get(CONF_STRATEGY, DEFAULT_STRATEGY))
        min_discharge_power = float(
            self.config.get(CONF_MIN_DISCHARGE_POWER, DEFAULT_MIN_DISCHARGE_POWER)
        )
        evening_target_soc = float(
            self.config.get(CONF_EVENING_TARGET_SOC, DEFAULT_EVENING_TARGET_SOC)
        )
        evening_target_hours = float(
            self.config.get(CONF_EVENING_TARGET_HOURS, DEFAULT_EVENING_TARGET_HOURS)
        )
        pv_day_factor = float(
            self.config.get(CONF_PV_DAY_FACTOR, DEFAULT_PV_DAY_FACTOR)
        )
        discharge_buffer_power = float(
            self.config.get(CONF_DISCHARGE_BUFFER_POWER, DEFAULT_DISCHARGE_BUFFER_POWER)
        )
        sunset_time = self._read_sunset()

        data = EnergyData(
            soc=soc,
            pv_power=pv_power,
            pv_remaining=pv_remaining,
            house_power=house_power,
            price=price,
            max_power=max_power,
            battery_capacity=battery_capacity,
            min_soc=min_soc,
            target_soc=target_soc,
            charge_efficiency=charge_efficiency,
            discharge_efficiency=discharge_efficiency,
            strategy=strategy,
            min_discharge_power=min_discharge_power,
            evening_target_soc=evening_target_soc,
            evening_target_hours=evening_target_hours,
            pv_day_factor=pv_day_factor,
            discharge_buffer_power=discharge_buffer_power,
            sunset_time=sunset_time,
        )

        _LOGGER.debug("EnergyData: %s", data)
        return data
