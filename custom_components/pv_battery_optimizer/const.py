DOMAIN = "pv_battery_optimizer"

# Config / Options Keys
CONF_BATTERY_SOC = "battery_soc"
CONF_POWER_LIMIT = "power_limit"
CONF_NORDPOOL = "nordpool"
CONF_HOUSE_POWER = "house_power"
CONF_PV_POWER = "pv_power"
CONF_PV_REMAINING = "pv_remaining"

CONF_BATTERY_CAPACITY = "battery_capacity"
CONF_MIN_SOC = "min_soc"
CONF_TARGET_SOC = "target_soc"
CONF_CHARGE_EFFICIENCY = "charge_efficiency"
CONF_DISCHARGE_EFFICIENCY = "discharge_efficiency"
CONF_MIN_DISCHARGE_POWER = "min_discharge_power"
CONF_EVENING_TARGET_SOC = "evening_target_soc"
CONF_EVENING_TARGET_HOURS = "evening_target_hours"
CONF_PV_DAY_FACTOR = "pv_day_factor"
CONF_DISCHARGE_BUFFER_POWER = "discharge_buffer_power"

CONF_LANGUAGE = "language"
CONF_STRATEGY = "strategy"
CONF_WRITE_TO_SENSOR = "write_to_sensor"

STRATEGY_SELF_CONSUMPTION = "self_consumption"
STRATEGY_DYNAMIC_PRICES = "dynamic_prices"
STRATEGY_GRID_FRIENDLY = "grid_friendly"
STRATEGY_EEG = "eeg_optimization"

DEFAULT_LANGUAGE = "de"
DEFAULT_STRATEGY = STRATEGY_EEG
DEFAULT_WRITE_TO_SENSOR = False
DEFAULT_BATTERY_CAPACITY = 10.24
DEFAULT_MIN_SOC = 10.0
DEFAULT_TARGET_SOC = 100.0
DEFAULT_CHARGE_EFFICIENCY = 95.0
DEFAULT_DISCHARGE_EFFICIENCY = 95.0
DEFAULT_MIN_DISCHARGE_POWER = 3000.0
DEFAULT_EVENING_TARGET_SOC = 85.0
DEFAULT_EVENING_TARGET_HOURS = 2.0
DEFAULT_PV_DAY_FACTOR = 1.5
DEFAULT_DISCHARGE_BUFFER_POWER = 500.0
DEFAULT_MAX_POWER_FALLBACK = 6000.0

# Sensor Keys
SENSOR_SOC = "soc"
SENSOR_PV_POWER = "pv_power"
SENSOR_PV_REMAINING = "pv_remaining"
SENSOR_HOUSE_POWER = "house_power"
SENSOR_PRICE = "price"
SENSOR_MAX_POWER = "max_power"
SENSOR_MISSING_ENERGY = "missing_energy"
SENSOR_PV_SURPLUS = "pv_surplus"
SENSOR_POSSIBLE_SOC = "possible_soc"
SENSOR_RECOMMENDATION = "recommendation"
SENSOR_CHARGE_SOURCE = "charge_source"
SENSOR_RECOMMENDATION_REASON = "recommendation_reason"
SENSOR_RECOMMENDED_CHARGE_POWER = "recommended_charge_power"
SENSOR_RECOMMENDED_CHARGE_POWER_EXACT = "recommended_charge_power_exact"
SENSOR_NEG_PRICE_HOURS_TODAY = "negative_price_hours_today"
SENSOR_NEG_PRICE_HOURS_TOMORROW = "negative_price_hours_tomorrow"
SENSOR_CAN_REACH_FULL = "can_reach_full"
