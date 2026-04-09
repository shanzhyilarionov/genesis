import random

import config
from core.life import Life
from core.world import (
    create_initial_food_grid,
    regenerate_food,
    create_trace_grid,
    decay_trace_grid,
)
import genetics.vm as vm
from genetics.vm import (
    MOVE_RANDOM,
    EAT_PLANT,
    MOVE_TOWARDS_PREY,
    REPRODUCE_OP,
    SENSE_FOOD,
    SENSE_PREY_DIRECTION,
    JUMP,
)


class GenesisSimulator:
    def __init__(self) -> None:
        self.food_grid = []
        self.trace_grid = []
        self.life_list = []
        self.tick = 0
        self.running = False

    def make_initial_genome_A(self, length: int = 32) -> list[int]:
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

    def make_initial_genome_B(self, length: int = 32) -> list[int]:
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

    def _spawn_initial_population(self) -> None:
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
                genome=self.make_initial_genome_A(),
            )
            self.life_list.append(organism)

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
                genome=self.make_initial_genome_B(),
            )
            self.life_list.append(organism)

    def _apply_predation(self, spatial: vm.SpatialIndex) -> None:
        for occupants in spatial.by_cell.values():
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
                predator.energy += config.PREDATION_ENERGY_GAIN_B
                spatial.remove(victim)

    def reset(self) -> None:
        self.food_grid = create_initial_food_grid()
        self.trace_grid = create_trace_grid()
        self.life_list = []
        self.tick = 0
        self.running = True
        config.global_pollution_level = 0.0
        self._spawn_initial_population()

    def step(self) -> None:
        if not self.running:
            return

        self.tick += 1

        living_count = len(self.life_list)
        pollution_increment = config.POLLUTION_INCREMENT_PER_LIFE * living_count
        config.global_pollution_level = min(
            config.global_pollution_level + pollution_increment,
            config.POLLUTION_CAP,
        )

        decay_trace_grid(self.trace_grid)

        new_offspring = []
        spatial = vm.SpatialIndex(self.life_list)

        for organism in self.life_list:
            vm.execute(
                organism,
                self.food_grid,
                spatial,
                self.trace_grid,
                new_offspring,
            )

        self.life_list.extend(new_offspring)
        self._apply_predation(spatial)
        self.life_list = [organism for organism in self.life_list if not organism.is_dead()]
        regenerate_food(self.food_grid)

        if not self.life_list:
            self.running = False

    def is_extinct(self) -> bool:
        return not self.life_list