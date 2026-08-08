from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_BATTERY_SOC,
    CONF_CHARGE_EFFICIENCY,
    CONF_DISCHARGE_BUFFER_POWER,
    CONF_DISCHARGE_EFFICIENCY,
    CONF_EVENING_TARGET_HOURS,
    CONF_EVENING_TARGET_SOC,
    CONF_HOUSE_POWER,
    CONF_LANGUAGE,
    CONF_MIN_DISCHARGE_POWER,
    CONF_MIN_SOC,
    CONF_NORDPOOL,
    CONF_POWER_LIMIT,
    CONF_PV_DAY_FACTOR,
    CONF_PV_POWER,
    CONF_PV_REMAINING,
    CONF_STRATEGY,
    CONF_TARGET_SOC,
    CONF_WRITE_TO_SENSOR,
    DEFAULT_BATTERY_CAPACITY,
    DEFAULT_CHARGE_EFFICIENCY,
    DEFAULT_DISCHARGE_BUFFER_POWER,
    DEFAULT_DISCHARGE_EFFICIENCY,
    DEFAULT_EVENING_TARGET_HOURS,
    DEFAULT_EVENING_TARGET_SOC,
    DEFAULT_LANGUAGE,
    DEFAULT_MIN_DISCHARGE_POWER,
    DEFAULT_MIN_SOC,
    DEFAULT_PV_DAY_FACTOR,
    DEFAULT_STRATEGY,
    DEFAULT_TARGET_SOC,
    DEFAULT_WRITE_TO_SENSOR,
    DOMAIN,
    STRATEGY_DYNAMIC_PRICES,
    STRATEGY_EEG,
    STRATEGY_GRID_FRIENDLY,
    STRATEGY_SELF_CONSUMPTION,
)


# ── Schema-Factories (eine pro Schritt) ──────────────────────────────────────

def _schema_step1(defaults: dict) -> vol.Schema:
    """Schritt 1: Sprache, Strategie und alle Sensor-Zuordnungen."""
    return vol.Schema(
        {
            vol.Required(
                CONF_LANGUAGE,
                default=defaults.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "de", "label": "Deutsch"},
                        {"value": "en", "label": "English"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_STRATEGY,
                default=defaults.get(CONF_STRATEGY, DEFAULT_STRATEGY),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": STRATEGY_EEG,
                         "label": "EEG-Vergütung optimieren"},
                        {"value": STRATEGY_SELF_CONSUMPTION,
                         "label": "Eigenverbrauch maximieren"},
                        {"value": STRATEGY_DYNAMIC_PRICES,
                         "label": "Dynamische Preise nutzen"},
                        {"value": STRATEGY_GRID_FRIENDLY,
                         "label": "Netzdienliches Verhalten"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_BATTERY_SOC,
                default=defaults.get(CONF_BATTERY_SOC),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                CONF_HOUSE_POWER,
                default=defaults.get(CONF_HOUSE_POWER),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                CONF_NORDPOOL,
                default=defaults.get(CONF_NORDPOOL),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                CONF_POWER_LIMIT,
                default=defaults.get(CONF_POWER_LIMIT),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="number")
            ),
            vol.Required(
                CONF_PV_POWER,
                default=defaults.get(CONF_PV_POWER),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                CONF_PV_REMAINING,
                default=defaults.get(CONF_PV_REMAINING, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=True)
            ),
            vol.Required(
                CONF_WRITE_TO_SENSOR,
                default=defaults.get(CONF_WRITE_TO_SENSOR, DEFAULT_WRITE_TO_SENSOR),
            ): selector.BooleanSelector(),
        }
    )


def _schema_step2(defaults: dict) -> vol.Schema:
    """Schritt 2: Batterie-Parameter."""
    return vol.Schema(
        {
            vol.Required(
                CONF_BATTERY_CAPACITY,
                default=defaults.get(CONF_BATTERY_CAPACITY, DEFAULT_BATTERY_CAPACITY),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1, max=100, step=0.1,
                    unit_of_measurement="kWh",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_MIN_SOC,
                default=defaults.get(CONF_MIN_SOC, DEFAULT_MIN_SOC),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=100, step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_TARGET_SOC,
                default=defaults.get(CONF_TARGET_SOC, DEFAULT_TARGET_SOC),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=50, max=100, step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_CHARGE_EFFICIENCY,
                default=defaults.get(CONF_CHARGE_EFFICIENCY, DEFAULT_CHARGE_EFFICIENCY),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=50, max=100, step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_DISCHARGE_EFFICIENCY,
                default=defaults.get(CONF_DISCHARGE_EFFICIENCY, DEFAULT_DISCHARGE_EFFICIENCY),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=50, max=100, step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


def _schema_step3(defaults: dict) -> vol.Schema:
    """Schritt 3: Strategie-Parameter."""
    return vol.Schema(
        {
            vol.Required(
                CONF_MIN_DISCHARGE_POWER,
                default=defaults.get(CONF_MIN_DISCHARGE_POWER, DEFAULT_MIN_DISCHARGE_POWER),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=6000, step=100,
                    unit_of_measurement="W",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_EVENING_TARGET_SOC,
                default=defaults.get(CONF_EVENING_TARGET_SOC, DEFAULT_EVENING_TARGET_SOC),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=50, max=100, step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_EVENING_TARGET_HOURS,
                default=defaults.get(CONF_EVENING_TARGET_HOURS, DEFAULT_EVENING_TARGET_HOURS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.5, max=6.0, step=0.5,
                    unit_of_measurement="h",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_PV_DAY_FACTOR,
                default=defaults.get(CONF_PV_DAY_FACTOR, DEFAULT_PV_DAY_FACTOR),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1.0, max=5.0, step=0.1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_DISCHARGE_BUFFER_POWER,
                default=defaults.get(CONF_DISCHARGE_BUFFER_POWER, DEFAULT_DISCHARGE_BUFFER_POWER),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=3000, step=100,
                    unit_of_measurement="W",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


# ── Ersteinrichtungs-Flow ─────────────────────────────────────────────────────

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Dreistufiger Konfigurationsablauf."""

    VERSION = 2

    def __init__(self) -> None:
        self._data: dict = {}

    async def async_step_user(self, user_input=None):
        """Schritt 1: Sensoren & Strategie."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_battery()

        return self.async_show_form(
            step_id="user",
            data_schema=_schema_step1(self._data),
        )

    async def async_step_battery(self, user_input=None):
        """Schritt 2: Batterie-Parameter."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_strategy()

        return self.async_show_form(
            step_id="battery",
            data_schema=_schema_step2(self._data),
        )

    async def async_step_strategy(self, user_input=None):
        """Schritt 3: Strategie-Parameter – Entry anlegen."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title="PV Battery Optimizer",
                data=self._data,
            )

        return self.async_show_form(
            step_id="strategy",
            data_schema=_schema_step3(self._data),
        )

    async def async_step_reconfigure(self, user_input=None):
        """Neukonfiguration Schritt 1."""
        entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        self._data = {
            **(entry.data if entry else {}),
            **(entry.options if entry else {}),
        }

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_reconfigure_battery()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_schema_step1(self._data),
        )

    async def async_step_reconfigure_battery(self, user_input=None):
        """Neukonfiguration Schritt 2."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_reconfigure_strategy()

        return self.async_show_form(
            step_id="reconfigure_battery",
            data_schema=_schema_step2(self._data),
        )

    async def async_step_reconfigure_strategy(self, user_input=None):
        """Neukonfiguration Schritt 3 – Entry aktualisieren."""
        entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        if user_input is not None:
            self._data.update(user_input)
            return self.async_update_reload_and_abort(
                entry,
                data=self._data,
                options={},
                reason="reconfigure_successful",
            )

        return self.async_show_form(
            step_id="reconfigure_strategy",
            data_schema=_schema_step3(self._data),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlow(config_entry)


# ── Options-Flow ──────────────────────────────────────────────────────────────

class OptionsFlow(config_entries.OptionsFlow):
    """Dreistufiger Options-Flow."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry
        self._data: dict = {}

    def _defaults(self) -> dict:
        return {
            **self.config_entry.data,
            **self.config_entry.options,
        }

    async def async_step_init(self, user_input=None):
        """Schritt 1: Sensoren & Strategie."""
        self._data = self._defaults()

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_battery()

        return self.async_show_form(
            step_id="init",
            data_schema=_schema_step1(self._data),
        )

    async def async_step_battery(self, user_input=None):
        """Schritt 2: Batterie-Parameter."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_strategy()

        return self.async_show_form(
            step_id="battery",
            data_schema=_schema_step2(self._data),
        )

    async def async_step_strategy(self, user_input=None):
        """Schritt 3: Strategie-Parameter – speichern."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)

        return self.async_show_form(
            step_id="strategy",
            data_schema=_schema_step3(self._data),
        )
