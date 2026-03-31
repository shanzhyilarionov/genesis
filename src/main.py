import sys
sys.dont_write_bytecode = True

import random
import time

import config
from core.life import Life
from core.world import (
    create_initial_food_grid,
    regenerate_food,
    create_trace_grid,
    decay_trace_grid,
)
import genetics.gene_vm as gene_vm
from genetics.gene_vm import (
    MOVE_RANDOM,
    EAT_PLANT,
    MOVE_TOWARDS_PREY,
    REPRODUCE_OP,
    SENSE_FOOD,
    SENSE_PREY_DIRECTION,
    JUMP,
)
from ui.state import build_web_frame, write_web_state
from ui.runtime import ensure_web_assets, start_web_server, open_browser


def make_initial_genome_A(length: int = 32) -> list[int]:
    base = [
        SENSE_FOOD,
        EAT_PLANT,
        MOVE_RANDOM,
        REPRODUCE_OP,
        JUMP,
        0,
    ]
    genome = []
    while len(genome) < length:
        genome.extend(base)
    return genome[:length]


def make_initial_genome_B(length: int = 32) -> list[int]:
    base = [
        SENSE_PREY_DIRECTION,
        MOVE_TOWARDS_PREY,
        MOVE_TOWARDS_PREY,
        MOVE_TOWARDS_PREY,
        REPRODUCE_OP,
        JUMP,
        0,
    ]
    genome = []
    while len(genome) < length:
        genome.extend(base)
    return genome[:length]


def _spawn_initial_population(life_list) -> None:
    params_A = config.SPECIES_PARAMETERS[config.SPECIES_A]
    for _ in range(config.INITIAL_POPULATION_A):
        x = random.randint(0, config.WORLD_WIDTH - 1)
        y = random.randint(0, config.WORLD_HEIGHT - 1)
        organism = Life(
            x=x,
            y=y,
            energy=random.randint(params_A["energy_min"], params_A["energy_max"]),
            lifespan=random.randint(
                params_A["lifespan_min"],
                params_A["lifespan_max"],
            ),
            metabolism=random.uniform(
                params_A["metabolism_min"],
                params_A["metabolism_max"],
            ),
            mobility=random.uniform(
                params_A["mobility_min"],
                params_A["mobility_max"],
            ),
            generation=0,
            species_id=config.SPECIES_A,
        )
        organism.genome = make_initial_genome_A()
        life_list.append(organism)

    params_B = config.SPECIES_PARAMETERS[config.SPECIES_B]
    for _ in range(config.INITIAL_POPULATION_B):
        x = random.randint(0, config.WORLD_WIDTH - 1)
        y = random.randint(0, config.WORLD_HEIGHT - 1)
        organism = Life(
            x=x,
            y=y,
            energy=random.randint(params_B["energy_min"], params_B["energy_max"]),
            lifespan=random.randint(
                params_B["lifespan_min"],
                params_B["lifespan_max"],
            ),
            metabolism=random.uniform(
                params_B["metabolism_min"],
                params_B["metabolism_max"],
            ),
            mobility=random.uniform(
                params_B["mobility_min"],
                params_B["mobility_max"],
            ),
            generation=0,
            species_id=config.SPECIES_B,
        )
        organism.genome = make_initial_genome_B()
        life_list.append(organism)


def _apply_predation(life_list) -> None:
    cell_map = {}

    for organism in life_list:
        key = (organism.x, organism.y)
        cell_map.setdefault(key, []).append(organism)

    for occupants in cell_map.values():
        predators = [
            o for o in occupants
            if o.species_id == config.SPECIES_B and not o.is_dead()
        ]
        prey = [
            o for o in occupants
            if o.species_id == config.SPECIES_A and not o.is_dead()
        ]

        if not predators or not prey:
            continue

        interactions = min(len(predators), len(prey))
        for i in range(interactions):
            predator = predators[i]
            victim = prey[i]
            victim.energy = 0.0
            victim.died_from_predation = True
            predator.energy += config.PREDATION_ENERGY_GAIN_B


def main() -> None:
    food_grid = create_initial_food_grid()
    trace_grid = create_trace_grid()
    life_list = []
    _spawn_initial_population(life_list)

    ensure_web_assets()

    initial_frame = build_web_frame(life_list, food_grid, 0)
    write_web_state(initial_frame)

    start_web_server()
    open_browser()

    for tick in range(1, config.MAX_TICK_COUNT + 1):

        living_count = len(life_list)
        pollution_increment = config.POLLUTION_INCREMENT_PER_LIFE * living_count
        config.global_pollution_level = min(
            config.global_pollution_level + pollution_increment,
            config.POLLUTION_CAP,
        )

        decay_trace_grid(trace_grid)
        new_offspring = []
        spatial = gene_vm.SpatialIndex(life_list)

        for organism in life_list:
            gene_vm.execute(organism, food_grid, spatial, trace_grid, new_offspring)

        life_list.extend(new_offspring)
        _apply_predation(life_list)

        life_list = [organism for organism in life_list if not organism.is_dead()]

        regenerate_food(food_grid)

        frame = build_web_frame(life_list, food_grid, tick)
        write_web_state(frame)

        if not life_list:
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