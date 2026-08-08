from datetime import datetime
import logging

from .const import (
    STRATEGY_DYNAMIC_PRICES,
    STRATEGY_EEG,
    STRATEGY_GRID_FRIENDLY,
    STRATEGY_SELF_CONSUMPTION,
)
from .sensor_reader import EnergyData

_LOGGER = logging.getLogger(__name__)

# PV gilt als aktiv ab dieser Schwelle in Watt
PV_ACTIVE_THRESHOLD_W = 200


class EnergyModel:
    """Berechnet Energiebedarf und Ladeempfehlungen."""

    def __init__(self, data: EnergyData) -> None:
        self.data = data

    # ------------------------------------------------------------------
    # Gemeinsame Hilfsmethoden
    # ------------------------------------------------------------------

    def missing_energy(self) -> float:
        """Energie in kWh, die bis Ziel-SOC fehlt (inkl. Ladeverlust)."""
        missing_percent = max(0.0, self.data.target_soc - self.data.soc)
        needed = missing_percent / 100 * self.data.battery_capacity
        return needed / (self.data.charge_efficiency / 100)

    def pv_surplus(self) -> float:
        """Aktueller PV-Ueberschuss in Watt."""
        return max(0.0, self.data.pv_power - self.data.house_power)

    def remaining_pv_energy(self) -> float:
        """Nach Ladeverlusten nutzbare PV-Restenergie in kWh."""
        return self.data.pv_remaining * (self.data.charge_efficiency / 100)

    def possible_soc_today(self) -> float:
        """Erreichbarer SOC aus der verbleibenden PV-Prognose."""
        added_soc = (
            self.remaining_pv_energy() / self.data.battery_capacity * 100
        )
        return min(self.data.target_soc, self.data.soc + added_soc)

    def can_reach_full(self) -> bool:
        """True wenn Ziel-SOC mit Rest-PV noch erreichbar ist."""
        return self.possible_soc_today() >= self.data.target_soc - 0.5

    def hours_until_sunset(self) -> float | None:
        """Stunden bis Sonnenuntergang, oder None wenn nicht bekannt."""
        if self.data.sunset_time is None:
            return None
        delta = (self.data.sunset_time - datetime.now()).total_seconds()
        return max(0.0, delta / 3600)

    def pv_is_active(self) -> bool:
        """True wenn nennenswerte PV-Produktion vorhanden ist."""
        return self.data.pv_power >= PV_ACTIVE_THRESHOLD_W

    def pv_day_mode_active(self) -> bool:
        """
        True wenn PV den Hausverbrauch um den konfigurierten Faktor
        ueberschreitet. Erst dann wechseln wir in den Tagesmodus.
        """
        if self.data.house_power <= 0:
            return self.data.pv_power >= PV_ACTIVE_THRESHOLD_W
        return self.data.pv_power >= self.data.house_power * self.data.pv_day_factor

    def _is_evening_phase(self) -> bool:
        """
        True wenn Sonnenuntergang vorbei ist und wir noch vor Mitternacht sind
        (Stunde >= 12 ohne PV -> Abend/Nacht nach Sonnenuntergang).
        Ab Mitternacht (Stunde < 12) gilt wieder Morgenphase.
        """
        if self.pv_is_active():
            return False
        return datetime.now().hour >= 12

    # ------------------------------------------------------------------
    # Strategie: EEG-Verguetung optimieren
    # ------------------------------------------------------------------
    #
    # Phasen (in dieser Reihenfolge geprueft):
    #
    # 0. SONDERREGEL  Negativer Preis  -> immer max_power
    # 1. ABENDPHASE   Kein PV, Stunde >= 12 -> safe_power
    # 2. NACHT/MORGEN Kein PV, Stunde < 12  -> safe_power
    # 3. MORGENPHASE  PV aktiv, PV < Haus * Faktor -> safe_power
    # 4. TAGESMODUS   PV >= Haus * Faktor:
    #    3a. PV < Haus (Wolke)            -> Haus + Puffer
    #    3b. Batterie-Ziel erreicht     -> safe_power
    #    3c. Mindest-SOC unterschritten -> PV-Ueberschuss
    #    3d. Abend-Fenster aktiv        -> berechnete Abendladung (gleimäßig)
    #    3e. Abend-Ziel erreicht        -> max_power (volle Leistung)
    # ------------------------------------------------------------------

    def _eeg_safe_power(self) -> float:
        """Mindestleistung zum Schutz der Entladefaehigkeit."""
        return self.data.min_discharge_power

    def _eeg_floor(self) -> float:
        """
        Floor fuer den Tagesmodus.
        Mit PV-Ueberschuss laed die Batterie – kein Entladeschutz noetig.
        Ohne PV-Ueberschuss muss der Wechselrichter entladen koennen.
        """
        if self.pv_surplus() > 0:
            return 0.0
        return self.data.min_discharge_power

    def _round_power(self, power: float) -> float:
        """
        Rundet auf 500-W-Schritte innerhalb der erlaubten Grenzen.
        Rundet kaufmaennisch — danach wird der Floor nochmals durchgesetzt,
        damit das Runden nicht unter min_discharge_power faellt.
        """
        step = 500.0
        rounded = round(power / step) * step
        clamped = max(0.0, min(self.data.max_power, rounded))
        # Floor nochmals pruefen: Runden koennte unter den konfigurierten
        # Entladeschutz gefallen sein (z.B. 3200 W -> 3000 W < floor 3200 W)
        floor = self._eeg_floor()
        if floor > 0 and clamped < floor:
            return floor
        return clamped

    def _eeg_evening_target_reached(self) -> bool:
        return self.data.soc >= self.data.evening_target_soc

    def _eeg_evening_charge_power(self, hours_left: float) -> float:
        """
        Gleichmaessig verteilte Ladeleistung fuer das Abend-Fenster.
        Ziel: evening_target_soc mit der verfuegbaren Zeit erreichen.
        """
        missing_percent = max(0.0, self.data.evening_target_soc - self.data.soc)
        missing_kwh = (
            missing_percent / 100
            * self.data.battery_capacity
            / (self.data.charge_efficiency / 100)
        )
        # Verfuegbare Ladezeit = Zeit bis Abend-Fenster beginnt
        available_hours = max(0.25, hours_left - self.data.evening_target_hours)
        return min(self.data.max_power, missing_kwh * 1000 / available_hours)

    def _eeg_recommendation(self) -> dict:
        result = self._eeg_recommendation_raw()
        result["recommended_power_exact"] = result["recommended_power"]
        result["recommended_power"] = self._round_power(
            result["recommended_power"]
        )
        return result

    def _eeg_final_charge_power(self, hours_left: float) -> float:
        """
        Nach Erreichen des Abend-Ziels wird mit voller Leistung
        (max_power) auf target_soc geladen.
        """
        return self.data.max_power

    def _eeg_recommendation_raw(self) -> dict:
        hours_left = self.hours_until_sunset()

        # 0. Negativer Boersenpreis: laden bis evening_target_soc
        # Bei None (Sensor unavailable) Preisoptimierung überspringen
        if self.data.price is not None and self.data.price < 0:
            if self.data.soc >= self.data.evening_target_soc:
                # Abend-Ziel bereits erreicht: kein weiteres Laden
                # Mit PV-Ueberschuss kein Entladeschutz noetig
                return {
                    "action": "wait",
                    "source": "none",
                    "reason": "battery_target_reached",
                    "recommended_power": self._eeg_floor(),
                    "should_charge_from_grid": False,
                }
            # Noch nicht am Ziel: PV-Ueberschuss maximal nutzen
            return {
                "action": "charge",
                "source": "pv",
                "reason": "negative_price_max_charge",
                "recommended_power": min(self.pv_surplus(), self.data.max_power),
                "should_charge_from_grid": False,
            }

        # Sunset unbekannt: sicher auf Mindestleistung bleiben
        if hours_left is None:
            return {
                "action": "wait",
                "source": "none",
                "reason": "sunset_unknown",
                "recommended_power": self._eeg_safe_power(),
                "should_charge_from_grid": False,
            }

        # 1+2. Kein PV -> Abend- oder Morgenphase je nach Uhrzeit
        if not self.pv_is_active():
            if self._is_evening_phase():
                return {
                    "action": "wait",
                    "source": "none",
                    "reason": "evening_discharge_phase",
                    "recommended_power": self._eeg_safe_power(),
                    "should_charge_from_grid": False,
                }
            return {
                "action": "wait",
                "source": "none",
                "reason": "no_pv_discharge_protection",
                "recommended_power": self._eeg_safe_power(),
                "should_charge_from_grid": False,
            }

        # 3. Morgenphase: PV laeuft, aber Tagesmodus noch nicht freigegeben
        #    (PV ueberschreitet Hausverbrauch noch nicht um den Faktor)
        if not self.pv_day_mode_active():
            # Sonderfall: PV vorhanden aber unter Hausverbrauch (tiefe Bewölkung)
            # -> Entladeschutz + Puffer damit kein Netzbezug entsteht
            if self.data.pv_power < self.data.house_power:
                protection = self.data.house_power + self.data.discharge_buffer_power
                return {
                    "action": "wait",
                    "source": "none",
                    "reason": "pv_below_house_power",
                    "recommended_power": max(protection, self._eeg_safe_power()),
                    "should_charge_from_grid": False,
                }
            return {
                "action": "wait",
                "source": "none",
                "reason": "morning_discharge_phase",
                "recommended_power": self._eeg_safe_power(),
                "should_charge_from_grid": False,
            }

        # 4. TAGESMODUS

        # 4a. Batterie-Ziel bereits erreicht
        if self.data.soc >= self.data.target_soc:
            return {
                "action": "wait",
                "source": "none",
                "reason": "battery_target_reached",
                "recommended_power": self._eeg_floor(),
                "should_charge_from_grid": False,
            }

        # 3c. Mindest-SOC unterschritten: sofort mit PV-Ueberschuss laden
        if self.data.soc <= self.data.min_soc:
            power = min(self.pv_surplus(), self.data.max_power)
            return {
                "action": "charge",
                "source": "pv",
                "reason": "minimum_soc_protection",
                "recommended_power": max(power, self._eeg_floor()),
                "should_charge_from_grid": False,
            }

        # 3d. Abend-Fenster: gezielt auf evening_target_soc aufladen (gleichmäßig verteilt)
        if not self._eeg_evening_target_reached():
            charge_power = self._eeg_evening_charge_power(hours_left)
            return {
                "action": "charge",
                "source": "pv",
                "reason": "evening_target_charge",
                "recommended_power": max(charge_power, self._eeg_floor()),
                "should_charge_from_grid": False,
            }

        # 3e. Abend-Ziel erreicht: jetzt auf target_soc (100 %) laden mit voller Leistung.
        charge_power = self._eeg_final_charge_power(hours_left)
        return {
            "action": "charge",
            "source": "pv",
            "reason": "evening_target_charge",
            "recommended_power": max(charge_power, self._eeg_floor()),
            "should_charge_from_grid": False,
        }

    # ------------------------------------------------------------------
    # Strategie-Platzhalter
    # ------------------------------------------------------------------

    def _self_consumption_recommendation(self) -> dict:
        return {
            "action": "wait",
            "source": "none",
            "reason": "strategy_not_implemented",
            "recommended_power": 0.0,
            "should_charge_from_grid": False,
        }

    def _dynamic_prices_recommendation(self) -> dict:
        return {
            "action": "wait",
            "source": "none",
            "reason": "strategy_not_implemented",
            "recommended_power": 0.0,
            "should_charge_from_grid": False,
        }

    def _grid_friendly_recommendation(self) -> dict:
        return {
            "action": "wait",
            "source": "none",
            "reason": "strategy_not_implemented",
            "recommended_power": 0.0,
            "should_charge_from_grid": False,
        }

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def recommendation(self) -> dict:
        """Ladeempfehlung der konfigurierten Strategie."""
        strategy = self.data.strategy

        if strategy == STRATEGY_EEG:
            return self._eeg_recommendation()
        if strategy == STRATEGY_SELF_CONSUMPTION:
            return self._self_consumption_recommendation()
        if strategy == STRATEGY_DYNAMIC_PRICES:
            return self._dynamic_prices_recommendation()
        if strategy == STRATEGY_GRID_FRIENDLY:
            return self._grid_friendly_recommendation()

        _LOGGER.warning(
            "Unbekannte Strategie '%s' – EEG wird als Fallback verwendet", strategy
        )
        return self._eeg_recommendation()