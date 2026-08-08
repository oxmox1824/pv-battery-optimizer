from .const import DEFAULT_LANGUAGE


TEXT = {
    "de": {
        "soc": "PV Battery Optimizer Batterie-SOC",
        "pv_power": "PV Battery Optimizer PV-Leistung",
        "pv_remaining": "PV Battery Optimizer PV-Restenergie heute",
        "house_power": "PV Battery Optimizer Hausverbrauch",
        "price": "PV Battery Optimizer Strompreis",
        "max_power": "PV Battery Optimizer Maximale Ladeleistung",
        "missing_energy": "PV Battery Optimizer Fehlende Batterieenergie",
        "pv_surplus": "PV Battery Optimizer PV-Überschuss",
        "possible_soc": "PV Battery Optimizer Möglicher SOC heute",
        "recommendation": "PV Battery Optimizer Ladeempfehlung",
        "charge_source": "PV Battery Optimizer Energiequelle",
        "recommendation_reason": "PV Battery Optimizer Begründung",
        "recommended_charge_power": (
            "PV Battery Optimizer Empfohlene Ladeleistung"
        ),
        "can_reach_full": (
            "PV Battery Optimizer Batterie heute voll erreichbar"
        ),
        "action_charge": "Laden",
        "action_wait": "Warten",
        "source_pv": "PV",
        "source_grid": "Netz",
        "source_none": "Keine",
        "yes": "Ja",
        "no": "Nein",
        "unknown": "Unbekannt",
        "battery_target_reached": "Batterie-Ziel erreicht",
        "minimum_soc_protection": "Mindest-SOC-Schutz",
        "negative_price_max_charge": "Negativer Börsenpreis – maximales Laden",
        "no_pv_discharge_protection": "Kein PV – Entladefähigkeit gesichert",
        "evening_discharge_phase": "Abendphase – Akku entladen",
        "morning_discharge_phase": "Morgenphase – Akku entladen",
        "evening_target_charge": "Abend-Ziel aufladen",
        "pv_below_house_power": "PV unter Hausverbrauch – Entladeschutz",
        "day_slow_charge": "Tagesmodus – langsames Laden",
        "sunset_unknown": "Sonnenuntergang unbekannt",
        "strategy_not_implemented": "Strategie nicht implementiert",
    },
    "en": {
        "soc": "PV Battery Optimizer Battery SOC",
        "pv_power": "PV Battery Optimizer PV Power",
        "pv_remaining": "PV Battery Optimizer PV Remaining Today",
        "house_power": "PV Battery Optimizer House Power",
        "price": "PV Battery Optimizer Electricity Price",
        "max_power": "PV Battery Optimizer Maximum Charge Power",
        "missing_energy": "PV Battery Optimizer Missing Battery Energy",
        "pv_surplus": "PV Battery Optimizer PV Surplus",
        "possible_soc": "PV Battery Optimizer Possible SOC Today",
        "recommendation": "PV Battery Optimizer Recommendation",
        "charge_source": "PV Battery Optimizer Charge Source",
        "recommendation_reason": (
            "PV Battery Optimizer Recommendation Reason"
        ),
        "recommended_charge_power": (
            "PV Battery Optimizer Recommended Charge Power"
        ),
        "can_reach_full": (
            "PV Battery Optimizer Can Reach Full Today"
        ),
        "action_charge": "Charge",
        "action_wait": "Wait",
        "source_pv": "PV",
        "source_grid": "Grid",
        "source_none": "None",
        "yes": "Yes",
        "no": "No",
        "unknown": "Unknown",
        "battery_target_reached": "Battery Target Reached",
        "minimum_soc_protection": "Minimum SOC Protection",
        "negative_price_max_charge": "Negative Price – Maximum Charging",
        "no_pv_discharge_protection": "No PV – Discharge Capacity Protected",
        "evening_discharge_phase": "Evening Phase – Discharging Battery",
        "morning_discharge_phase": "Morning Phase – Discharging Battery",
        "evening_target_charge": "Charging to Evening Target",
        "pv_below_house_power": "PV Below House Consumption – Discharge Protection",
        "day_slow_charge": "Day Mode – Slow Charging",
        "sunset_unknown": "Sunset Time Unknown",
        "strategy_not_implemented": "Strategy Not Implemented",
    },
}


def text(
    language: str | None,
    key: str,
) -> str:
    """Gib den übersetzten Text zurück."""
    translations = TEXT.get(
        language,
        TEXT[DEFAULT_LANGUAGE],
    )

    return translations.get(
        key,
        key,
    )