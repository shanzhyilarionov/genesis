import sys
sys.dont_write_bytecode = True

import argparse
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

    run_dir = Path(output_dir) / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    sim.stats.export_history_csv(run_dir / "history.csv")
    sim.stats.export_summary_json(
        run_dir / "summary.json",
        metadata={
            "seed": seed,
            "max_ticks": max_ticks,
            "final_tick": sim.tick,
            "extinct": sim.is_extinct(),
        },
    )

    print(f"Finished seed={seed}, tick={sim.tick}, extinct={sim.is_extinct()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--max-ticks", type=int, default=config.MAX_TICK_COUNT)
    parser.add_argument("--output-dir", type=str, default="results")
    args = parser.parse_args()

    for i in range(args.runs):
        seed = args.seed + i
        run_once(seed, args.max_ticks, args.output_dir)


if __name__ == "__main__":
    main()