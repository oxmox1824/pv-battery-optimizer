from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_LANGUAGE, DEFAULT_LANGUAGE, DOMAIN
from .language import text as _t


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Richte die PV-Battery-Optimizer-Sensoren ein."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="soc",
                unique_id="pv_battery_optimizer_soc",
                name="PV Battery Optimizer Battery SOC",
                unit="%",
                device_class=SensorDeviceClass.BATTERY,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="pv_power",
                unique_id="pv_battery_optimizer_pv_power",
                name="PV Battery Optimizer PV Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="pv_remaining",
                unique_id="pv_battery_optimizer_pv_remaining",
                name="PV Battery Optimizer PV Remaining Today",
                unit="kWh",
                device_class=SensorDeviceClass.ENERGY,
                state_class=SensorStateClass.TOTAL,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="house_power",
                unique_id="pv_battery_optimizer_house_power",
                name="PV Battery Optimizer House Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="price",
                unique_id="pv_battery_optimizer_price",
                name="PV Battery Optimizer Electricity Price",
                unit="ct/kWh",
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="max_power",
                unique_id="pv_battery_optimizer_max_charge_power",
                name="PV Battery Optimizer Maximum Charge Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="missing_energy",
                unique_id="pv_battery_optimizer_missing_energy",
                name="PV Battery Optimizer Missing Battery Energy",
                unit="kWh",
                device_class=SensorDeviceClass.ENERGY,
                state_class=SensorStateClass.TOTAL,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="pv_surplus",
                unique_id="pv_battery_optimizer_pv_surplus",
                name="PV Battery Optimizer PV Surplus",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="possible_soc",
                unique_id="pv_battery_optimizer_possible_soc_today",
                name="PV Battery Optimizer Possible SOC Today",
                unit="%",
                device_class=SensorDeviceClass.BATTERY,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key="recommendation",
                unique_id="pv_battery_optimizer_recommendation",
                name="PV Battery Optimizer Recommendation",
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key="charge_source",
                unique_id="pv_battery_optimizer_charge_source",
                name="PV Battery Optimizer Charge Source",
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key="recommendation_reason",
                unique_id="pv_battery_optimizer_recommendation_reason",
                name="PV Battery Optimizer Recommendation Reason",
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="recommended_charge_power",
                unique_id="pv_battery_optimizer_recommended_charge_power",
                name="PV Battery Optimizer Recommended Charge Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="recommended_charge_power_exact",
                unique_id="pv_battery_optimizer_recommended_charge_power_exact",
                name="PV Battery Optimizer Recommended Charge Power Exact",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="negative_price_hours_today",
                unique_id="pv_battery_optimizer_negative_price_hours_today",
                name="PV Battery Optimizer Negative Price Hours Today",
                unit="h",
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key="negative_price_hours_tomorrow",
                unique_id="pv_battery_optimizer_negative_price_hours_tomorrow",
                name="PV Battery Optimizer Negative Price Hours Tomorrow",
                unit="h",
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key="can_reach_full",
                unique_id="pv_battery_optimizer_can_reach_full_today",
                name="PV Battery Optimizer Can Reach Full Today",
                boolean_as_text=True,
            ),
        ]
    )


class PVBatteryOptimizerValueSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Stellt einen numerischen Coordinator-Wert bereit."""

    def __init__(
        self,
        coordinator,
        key: str,
        unique_id: str,
        name: str,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
    ) -> None:
        """Initialisiere den Sensor."""
        super().__init__(coordinator)

        self._key = key
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Gib den aktuellen Coordinator-Wert zurück."""
        return (self.coordinator.data or {}).get(
            self._key,
        )


class PVBatteryOptimizerTextSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Stellt einen Text- oder Statuswert aus dem Coordinator bereit."""

    def __init__(
        self,
        coordinator,
        key: str,
        unique_id: str,
        name: str,
        boolean_as_text: bool = False,
    ) -> None:
        """Initialisiere den Sensor."""
        super().__init__(coordinator)

        self._key = key
        self._boolean_as_text = boolean_as_text
        self._attr_unique_id = unique_id
        self._attr_name = name

    @property
    def native_value(self) -> str:
        """Gib den aktuellen Coordinator-Wert lesbar zurück."""
        value = (self.coordinator.data or {}).get(self._key)
        lang = self.coordinator.config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)

        if self._boolean_as_text:
            return _t(lang, "yes") if value else _t(lang, "no")

        if value is None:
            return _t(lang, "unknown")

        return str(value)