import sys
sys.dont_write_bytecode = True

import time
import config
from core.simulator import GenesisSimulator
from ui.window import GenesisWindow

def main() -> None:
    sim = GenesisSimulator()
    sim.reset()

    window = GenesisWindow()
    window.render(sim.life_list, sim.food_grid)

    try:
        while sim.running and sim.tick < config.MAX_TICK_COUNT:
            if not window.process_events():
                break

            sim.step()
            window.render(sim.life_list, sim.food_grid)

            if sim.is_extinct():
                print("All organisms died, simulation terminated.")
                break

            time.sleep(config.TICK_DELAY_SECONDS)
        else:
            print(f"Reached maximum tick count {config.MAX_TICK_COUNT}, simulation terminated.")
    finally:
        window.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")