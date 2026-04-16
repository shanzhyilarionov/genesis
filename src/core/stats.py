from dataclasses import dataclass, asdict
import csv
import json
from pathlib import Path
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
    birth_a: int
    birth_b: int
    death_a: int
    death_b: int
    avg_age_a: float
    avg_age_b: float
    avg_energy_a: float
    avg_energy_b: float
    avg_metabolism_a: float
    avg_metabolism_b: float
    intrinsic_death_a: int
    intrinsic_death_b: int
    starvation_death_a: int
    starvation_death_b: int
    predation_death_a: int
    pollution_death_a: int
    pollution_death_b: int
    mutations_a: int
    mutations_b: int
    dominant_opcode_a: int | None
    dominant_opcode_b: int | None


class StatsCollector:
    def __init__(self) -> None:
        self.history: list[StatsSnapshot] = []

    def reset(self) -> None:
        self.history.clear()

    def _mean(self, values) -> float:
        return sum(values) / len(values) if values else 0.0

    def _dominant_opcode(self, counts: dict[int, int]) -> int | None:
        if not counts:
            return None
        return max(counts.items(), key=lambda item: (item[1], -item[0]))[0]

    def capture(self, simulator) -> None:
        life_list = simulator.life_list
        food_grid = simulator.food_grid
        tick_stats = getattr(simulator, "tick_stats", {})

        a_list = [o for o in life_list if o.species_id == config.SPECIES_A]
        b_list = [o for o in life_list if o.species_id == config.SPECIES_B]

        food_total = sum(sum(row) for row in food_grid)

        birth_a = tick_stats.get("birth_a", 0)
        birth_b = tick_stats.get("birth_b", 0)
        death_a = tick_stats.get("death_a", 0)
        death_b = tick_stats.get("death_b", 0)

        snapshot = StatsSnapshot(
            tick=simulator.tick,
            population_total=len(life_list),
            population_a=len(a_list),
            population_b=len(b_list),
            food_total=food_total,
            pollution=config.global_pollution_level,
            births=birth_a + birth_b,
            deaths=death_a + death_b,
            birth_a=birth_a,
            birth_b=birth_b,
            death_a=death_a,
            death_b=death_b,
            avg_age_a=self._mean([o.age_ticks for o in a_list]),
            avg_age_b=self._mean([o.age_ticks for o in b_list]),
            avg_energy_a=self._mean([o.energy for o in a_list]),
            avg_energy_b=self._mean([o.energy for o in b_list]),
            avg_metabolism_a=self._mean([o.metabolism_rate for o in a_list]),
            avg_metabolism_b=self._mean([o.metabolism_rate for o in b_list]),
            intrinsic_death_a=tick_stats.get("intrinsic_death_a", 0),
            intrinsic_death_b=tick_stats.get("intrinsic_death_b", 0),
            starvation_death_a=tick_stats.get("starvation_death_a", 0),
            starvation_death_b=tick_stats.get("starvation_death_b", 0),
            predation_death_a=tick_stats.get("predation_death_a", 0),
            pollution_death_a=tick_stats.get("pollution_death_a", 0),
            pollution_death_b=tick_stats.get("pollution_death_b", 0),
            mutations_a=tick_stats.get("mutations_a", 0),
            mutations_b=tick_stats.get("mutations_b", 0),
            dominant_opcode_a=self._dominant_opcode(
                tick_stats.get("opcode_counts_a", {})
            ),
            dominant_opcode_b=self._dominant_opcode(
                tick_stats.get("opcode_counts_b", {})
            ),
        )
        self.history.append(snapshot)

    def export_history_csv(self, path: str) -> None:
        if not self.history:
            return

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        rows = [asdict(snapshot) for snapshot in self.history]
        fieldnames = list(rows[0].keys())

        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def export_summary_json(self, path: str, metadata: dict | None = None) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        final_snapshot = asdict(self.history[-1]) if self.history else None

        payload = {
            "metadata": metadata or {},
            "final_snapshot": final_snapshot,
            "num_snapshots": len(self.history),
        }

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)