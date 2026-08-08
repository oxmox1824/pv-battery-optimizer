from dataclasses import dataclass


@dataclass
class EnergyData:

    soc: float

    pv_power: float

    pv_remaining: float

    house_power: float

    price: float

    max_power: float = 6000


@dataclass
class OptimizationResult:

    recommended_power: int

    target_soc: float

    missing_energy: float

    pv_surplus: float

    reason: str