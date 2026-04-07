import sys
sys.dont_write_bytecode = True

import time

import config
from core.simulator import GenesisSimulator
from ui.state import build_web_frame, write_web_state
from ui.runtime import ensure_web_assets, start_web_server, open_browser


def main() -> None:
    sim = GenesisSimulator()
    sim.reset()

    ensure_web_assets()

    initial_frame = build_web_frame(sim.life_list, sim.food_grid, 0)
    write_web_state(initial_frame)

    start_web_server()
    open_browser()

    while sim.running and sim.tick < config.MAX_TICK_COUNT:
        sim.step()

        frame = build_web_frame(sim.life_list, sim.food_grid, sim.tick)
        write_web_state(frame)

        if sim.is_extinct():
            print("All organisms died, simulation terminated.")
            break

        time.sleep(config.TICK_DELAY_SECONDS)
    else:
        print(f"Reached maximum tick count {config.MAX_TICK_COUNT}, simulation terminated.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")