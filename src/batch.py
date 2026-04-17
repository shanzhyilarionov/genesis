import sys
sys.dont_write_bytecode = True

import random
from pathlib import Path

import config
from core.simulator import GenesisSimulator


def run_once(seed: int, max_ticks: int, output_dir: str) -> None:
    random.seed(seed)

    sim = GenesisSimulator()
    sim.reset()

    while sim.running and sim.tick < max_ticks:
        sim.step()
        if sim.is_extinct():
            break

    output_path = Path(output_dir) / f"seed_{seed}.csv"
    sim.stats.export_history_csv(output_path)

    print(f"Completed  Seed = {seed}  Tick = {sim.tick}  Extinct = {sim.is_extinct()}")


def main() -> None:
    seed = int(input("Seed: ").strip())
    runs = int(input("Runs: ").strip())

    max_ticks = config.MAX_TICK_COUNT
    output_dir = "results"

    for i in range(runs):
        current_seed = seed + i
        run_once(current_seed, max_ticks, output_dir)


if __name__ == "__main__":
    main()