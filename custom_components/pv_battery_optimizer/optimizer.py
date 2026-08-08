from datetime import datetime


BATTERY_CAPACITY = 10.0       # kWh
MAX_POWER = 6000              # W
MIN_DISCHARGE_LIMIT = 1500    # W

NEGATIVE_PRICE_LIMIT = 0.0


def calculate_power(
    soc,
    price,
    pv_now,
    pv_remaining,
    house_power,
    sunset,
):

    now = datetime.now()


    # ---------------------------------
    # Zeit bis Sonnenuntergang
    # ---------------------------------

    hours_left = (
        sunset - now
    ).total_seconds() / 3600


    if hours_left < 0.25:
        hours_left = 0.25


    # ---------------------------------
    # Fehlende Energie bis 100 %
    # ---------------------------------

    missing_kwh = (
        max(0, 100 - soc)
        /
        100
        *
        BATTERY_CAPACITY
    )


    # ---------------------------------
    # PV Überschuss
    # ---------------------------------

    pv_surplus = max(
        0,
        pv_now - house_power
    )


    # ---------------------------------
    # Erreichbarkeit 100 %
    # ---------------------------------

    expected_house_energy = (
        house_power
        *
        hours_left
        /
        1000
    )


    usable_pv = max(
        0,
        pv_remaining - expected_house_energy
    )


    possible_soc = (
        soc
        +
        usable_pv
        /
        BATTERY_CAPACITY
        *
        100
    )


    target_soc = min(
        100,
        possible_soc
    )


    # ---------------------------------
    # Basisladung
    # langsam über den Tag verteilt
    # ---------------------------------

    if missing_kwh > 0:

        base_power = (
            missing_kwh
            *
            1000
            /
            hours_left
        )

    else:

        base_power = 0


    reason = "Zeitgerechtes Laden"


    # ---------------------------------
    # Negative Preise
    # PV maximal nutzen
    # ---------------------------------

    if price < NEGATIVE_PRICE_LIMIT:

        if pv_surplus > 0:

            power = pv_surplus

            reason = (
                "Negativer Börsenpreis "
                "+ PV Überschuss"
            )

        else:

            power = base_power

            reason = (
                "Negativer Preis, "
                "warte auf PV"
            )


    # ---------------------------------
    # Normale Preise
    # ---------------------------------

    else:

        power = base_power


        # PV Überschuss darf unterstützen,
        # aber nicht unnötig schnell voll machen

        if pv_surplus > power:

            power = min(
                pv_surplus,
                power * 2
            )

            reason = (
                "PV angepasstes Laden"
            )


    # ---------------------------------
    # Entladefähigkeit erhalten
    # ---------------------------------

    # Da Sungrow diese Einstellung auch
    # auf Entladung anwendet:
    # niemals zu stark begrenzen

    if power < MIN_DISCHARGE_LIMIT:

        if soc > 20:

            power = max(
                power,
                MIN_DISCHARGE_LIMIT
            )


    # ---------------------------------
    # Grenzen
    # ---------------------------------

    power = max(
        0,
        min(
            MAX_POWER,
            power
        )
    )


    return {

        "power": int(
            round(power / 10) * 10
        ),

        "target_soc": round(
            target_soc,
            1
        ),

        "missing_kwh": round(
            missing_kwh,
            2
        ),

        "hours_left": round(
            hours_left,
            1
        ),

        "reason": reason,
    }