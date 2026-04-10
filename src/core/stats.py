from dataclasses import dataclass
import config

@dataclass
class StatsSnapshot:
    tick: int
    population_total: int
    population_a: int
    population_b: int
    food_total: int
    pollution: float
    births: int
    deaths: int
    avg_age_a: float
    avg_age_b: float
    avg_energy_a: float
    avg_energy_b: float


class StatsCollector:
    def __init__(self) -> None:
        self.history: list[StatsSnapshot] = []

    def reset(self) -> None:
        self.history.clear()

    def capture(self, simulator, births: int, deaths: int) -> None:
        life_list = simulator.life_list
        food_grid = simulator.food_grid

        a_list = [o for o in life_list if o.species_id == config.SPECIES_A]
        b_list = [o for o in life_list if o.species_id == config.SPECIES_B]

        food_total = sum(sum(row) for row in food_grid)

        avg_age_a = (
            sum(o.age_ticks for o in a_list) / len(a_list)
            if a_list else 0.0
        )
        avg_age_b = (
            sum(o.age_ticks for o in b_list) / len(b_list)
            if b_list else 0.0
        )

        avg_energy_a = (
            sum(o.energy for o in a_list) / len(a_list)
            if a_list else 0.0
        )
        avg_energy_b = (
            sum(o.energy for o in b_list) / len(b_list)
            if b_list else 0.0
        )

        snapshot = StatsSnapshot(
            tick=simulator.tick,
            population_total=len(life_list),
            population_a=len(a_list),
            population_b=len(b_list),
            food_total=food_total,
            pollution=config.global_pollution_level,
            births=births,
            deaths=deaths,
            avg_age_a=avg_age_a,
            avg_age_b=avg_age_b,
            avg_energy_a=avg_energy_a,
            avg_energy_b=avg_energy_b,
        )

        self.history.append(snapshot)