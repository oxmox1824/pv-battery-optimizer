from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
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
                key=SENSOR_SOC,
                unique_id="pv_battery_optimizer_soc",
                name="PV Battery Optimizer Battery SOC",
                unit="%",
                device_class=SensorDeviceClass.BATTERY,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_PV_POWER,
                unique_id="pv_battery_optimizer_pv_power",
                name="PV Battery Optimizer PV Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_PV_REMAINING,
                unique_id="pv_battery_optimizer_pv_remaining",
                name="PV Battery Optimizer PV Remaining Today",
                unit="kWh",
                device_class=SensorDeviceClass.ENERGY,
                state_class=SensorStateClass.TOTAL,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_HOUSE_POWER,
                unique_id="pv_battery_optimizer_house_power",
                name="PV Battery Optimizer House Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_PRICE,
                unique_id="pv_battery_optimizer_price",
                name="PV Battery Optimizer Electricity Price",
                unit="ct/kWh",
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_MAX_POWER,
                unique_id="pv_battery_optimizer_max_charge_power",
                name="PV Battery Optimizer Maximum Charge Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_MISSING_ENERGY,
                unique_id="pv_battery_optimizer_missing_energy",
                name="PV Battery Optimizer Missing Battery Energy",
                unit="kWh",
                device_class=SensorDeviceClass.ENERGY,
                state_class=SensorStateClass.TOTAL,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_PV_SURPLUS,
                unique_id="pv_battery_optimizer_pv_surplus",
                name="PV Battery Optimizer PV Surplus",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_POSSIBLE_SOC,
                unique_id="pv_battery_optimizer_possible_soc_today",
                name="PV Battery Optimizer Possible SOC Today",
                unit="%",
                device_class=SensorDeviceClass.BATTERY,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key=SENSOR_RECOMMENDATION,
                unique_id="pv_battery_optimizer_recommendation",
                name="PV Battery Optimizer Recommendation",
                translation_key="recommendation",
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key=SENSOR_CHARGE_SOURCE,
                unique_id="pv_battery_optimizer_charge_source",
                name="PV Battery Optimizer Charge Source",
                translation_key="charge_source",
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key=SENSOR_RECOMMENDATION_REASON,
                unique_id="pv_battery_optimizer_recommendation_reason",
                name="PV Battery Optimizer Recommendation Reason",
                translation_key="recommendation_reason",
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_RECOMMENDED_CHARGE_POWER,
                unique_id="pv_battery_optimizer_recommended_charge_power",
                name="PV Battery Optimizer Recommended Charge Power",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_RECOMMENDED_CHARGE_POWER_EXACT,
                unique_id="pv_battery_optimizer_recommended_charge_power_exact",
                name="PV Battery Optimizer Recommended Charge Power Exact",
                unit="W",
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_NEG_PRICE_HOURS_TODAY,
                unique_id="pv_battery_optimizer_negative_price_hours_today",
                name="PV Battery Optimizer Negative Price Hours Today",
                unit="h",
            ),
            PVBatteryOptimizerValueSensor(
                coordinator,
                key=SENSOR_NEG_PRICE_HOURS_TOMORROW,
                unique_id="pv_battery_optimizer_negative_price_hours_tomorrow",
                name="PV Battery Optimizer Negative Price Hours Tomorrow",
                unit="h",
            ),
            PVBatteryOptimizerTextSensor(
                coordinator,
                key=SENSOR_CAN_REACH_FULL,
                unique_id="pv_battery_optimizer_can_reach_full_today",
                name="PV Battery Optimizer Can Reach Full Today",
                translation_key="can_reach_full",
            ),
        ]
    )


class PVBatteryOptimizerValueSensor(CoordinatorEntity, SensorEntity):
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
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self._key)


class PVBatteryOptimizerTextSensor(CoordinatorEntity, SensorEntity):
    """Stellt einen Text- oder Statuswert aus dem Coordinator bereit."""

    def __init__(
        self,
        coordinator,
        key: str,
        unique_id="pv_battery_optimizer_text",
        name="Text Sensor",
        translation_key: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = unique_id
        self._attr_name = name
        if translation_key:
            self._attr_translation_key = translation_key

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get(self._key)
