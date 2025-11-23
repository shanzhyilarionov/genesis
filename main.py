import random
import time
import math
from collections import Counter

import config
from life import Life
from world import create_initial_food_grid, regenerate_food
from render import render, clear_screen
import gene_vm
from gene_vm import (
    MOVE_RANDOM,
    EAT_PLANT,
    MOVE_TOWARDS_PREY,
    REPRODUCE_OP,
    SENSE_FOOD,
    SENSE_PREY_DIRECTION,
    JUMP,
)

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
        REPRODUCE_OP,
        MOVE_RANDOM,
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
        config.total_spawned_A += 1

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
        config.total_spawned_B += 1

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

def _update_genome_stats(life_list) -> None:
    alive = [o for o in life_list if not o.is_dead()]
    alive_A = [o for o in alive if o.species_id == config.SPECIES_A]
    alive_B = [o for o in alive if o.species_id == config.SPECIES_B]
    
    def _stats(group):
        if not group:
            return 0, 0.0
        counter = Counter(tuple(o.genome) for o in group)
        unique = len(counter)
        total = len(group)
        entropy = 0.0
        for count in counter.values():
            p = count / total
            entropy -= p * math.log(p, 2)
        return unique, entropy
    
    uA, eA = _stats(alive_A)
    uB, eB = _stats(alive_B)
    config.unique_genomes_A = uA
    config.genome_diversity_A = eA
    config.unique_genomes_B = uB
    config.genome_diversity_B = eB

def _update_vm_stats() -> None:
    if gene_vm.active_count_A > 0:
        config.vm_idle_rate_A = gene_vm.idle_count_A / gene_vm.active_count_A
        config.mean_exec_length_A = gene_vm.total_steps_A / gene_vm.active_count_A
    else:
        config.vm_idle_rate_A = 0.0
        config.mean_exec_length_A = 0.0
    
    if gene_vm.active_count_B > 0:
        config.vm_idle_rate_B = gene_vm.idle_count_B / gene_vm.active_count_B
        config.mean_exec_length_B = gene_vm.total_steps_B / gene_vm.active_count_B
    else:
        config.vm_idle_rate_B = 0.0
        config.mean_exec_length_B = 0.0
    
    if any(gene_vm.opcode_counts_A):
        config.dominant_opcode_A = max(
            range(len(gene_vm.opcode_counts_A)),
            key=lambda i: gene_vm.opcode_counts_A[i],
        )
    else:
        config.dominant_opcode_A = 0
    
    if any(gene_vm.opcode_counts_B):
        config.dominant_opcode_B = max(
            range(len(gene_vm.opcode_counts_B)),
            key=lambda i: gene_vm.opcode_counts_B[i],
        )
    else:
        config.dominant_opcode_B = 0

def main() -> None:
    world_buffer = [
        [" " for _ in range(config.WORLD_WIDTH)]
        for _ in range(config.WORLD_HEIGHT)
    ]
    food_grid = create_initial_food_grid()
    life_list = []
    _spawn_initial_population(life_list)

    for tick in range(1, config.MAX_TICK_COUNT + 1):
        gene_vm.reset_vm_stats()
        living_count = len(life_list)
        pollution_increment = config.POLLUTION_INCREMENT_PER_LIFE * living_count
        config.global_pollution_level = min(
            config.global_pollution_level + pollution_increment,
            config.POLLUTION_CAP,
        )
        new_offspring = []

        for organism in life_list:
            gene_vm.execute(organism, food_grid, life_list, new_offspring)

        life_list.extend(new_offspring)
        _apply_predation(life_list)
        config.birth_A_tick = sum(
            1 for o in new_offspring if o.species_id == config.SPECIES_A
        )
        config.birth_B_tick = sum(
            1 for o in new_offspring if o.species_id == config.SPECIES_B
        )
        config.total_spawned_A += config.birth_A_tick
        config.total_spawned_B += config.birth_B_tick
        config.death_A_tick = 0
        config.death_B_tick = 0
        survivors = []

        for organism in life_list:
            if organism.is_dead():
                if organism.species_id == config.SPECIES_A:
                    config.death_A_tick += 1
                    if organism.age_ticks > organism.lifespan_ticks:
                        config.intrinsic_mortality_A += 1
                    elif organism.died_from_pollution:
                        config.pollution_mortality_A += 1
                    elif organism.died_from_predation:
                        config.predation_mortality_A += 1
                    elif organism.energy <= 0.0:
                        config.starvation_mortality_A += 1
                else:
                    config.death_B_tick += 1
                    if organism.age_ticks > organism.lifespan_ticks:
                        config.intrinsic_mortality_B += 1
                    elif organism.died_from_pollution:
                        config.pollution_mortality_B += 1
                    elif organism.died_from_predation:
                        config.predation_mortality_B += 1
                    elif organism.energy <= 0.0:
                        config.starvation_mortality_B += 1
            else:
                survivors.append(organism)

        life_list = survivors
        regenerate_food(food_grid)
        _update_genome_stats(life_list)
        _update_vm_stats()
        render(world_buffer, life_list, food_grid, tick)
        
        if not life_list:
            print("All organisms died, simulation terminated.")
            break
        time.sleep(config.TICK_DELAY_SECONDS)
        
    else:
        clear_screen()
        print(f"Reached maximum tick count {config.MAX_TICK_COUNT}, simulation terminated.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("Simulation interrupted by user.")