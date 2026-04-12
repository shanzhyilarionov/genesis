import random
import config
from core.life import Life
from genetics.opcodes import (
    NOP,
    MOVE_RANDOM,
    MOVE_TO_FOOD,
    EAT_PLANT,
    MOVE_TOWARDS_PREY,
    REPRODUCE_OP,
    SENSE_FOOD,
    SENSE_ENERGY_LOW,
    SENSE_NEIGHBOR,
    SENSE_RANDOM,
    SENSE_PREY,
    SENSE_PREY_DIRECTION,
    INC_R0,
    DEC_R0,
    COPY_R0_TO_R1,
    LOAD_R0,
    STORE_R0,
    JUMP,
    JUMP_IF_R0_ZERO,
    JUMP_IF_R0_NZ,
)
from genetics.spatial_index import SpatialIndex
from genetics.behaviors import (
    _move_random,
    _move_to_food,
    _eat_plant,
    _move_towards_prey,
    _sense_food,
    _sense_neighbor,
    _sense_prey,
    _sense_prey_direction,
    _try_reproduce,
)


def execute(
    life: Life,
    food_grid,
    spatial,
    trace_grid,
    offspring_list,
    tick_stats,
    max_steps: int = 5,
) -> None:
    if life.is_dead():
        return

    life.age_ticks += 1
    if life.age_ticks > life.lifespan_ticks:
        life.death_cause = "intrinsic"
        spatial.remove(life)
        return

    life.energy -= life.metabolism_rate
    if life.energy <= 0.0:
        life.death_cause = "starvation"
        spatial.remove(life)
        return

    if random.random() < 0.002 * config.global_pollution_level:
        life.energy = 0.0
        life.death_cause = "pollution"
        spatial.remove(life)
        return

    genome = life.genome
    n = len(genome)
    steps = 0

    while steps < max_steps and not life.is_dead():
        ip = life.ip % n
        opcode = genome[ip]

        if life.species_id == config.SPECIES_A:
            opcode_counts = tick_stats["opcode_counts_a"]
        else:
            opcode_counts = tick_stats["opcode_counts_b"]
        opcode_counts[opcode] = opcode_counts.get(opcode, 0) + 1

        if opcode == NOP:
            life.ip = (ip + 1) % n

        elif opcode == MOVE_RANDOM:
            _move_random(life, spatial)
            life.ip = (ip + 1) % n

        elif opcode == MOVE_TO_FOOD:
            _move_to_food(life, food_grid, spatial)
            life.ip = (ip + 1) % n

        elif opcode == EAT_PLANT:
            _eat_plant(life, food_grid)
            life.ip = (ip + 1) % n

        elif opcode == MOVE_TOWARDS_PREY:
            _move_towards_prey(life, spatial, trace_grid)
            life.ip = (ip + 1) % n

        elif opcode == REPRODUCE_OP:
            _try_reproduce(life, offspring_list, spatial)
            life.ip = (ip + 1) % n

        elif opcode == SENSE_FOOD:
            life.registers[0] = float(_sense_food(life, food_grid))
            life.ip = (ip + 1) % n

        elif opcode == SENSE_ENERGY_LOW:
            threshold = 10.0
            life.registers[1] = 1.0 if life.energy < threshold else 0.0
            life.ip = (ip + 1) % n

        elif opcode == SENSE_NEIGHBOR:
            life.registers[2] = float(_sense_neighbor(life, spatial))
            life.ip = (ip + 1) % n

        elif opcode == SENSE_RANDOM:
            life.registers[3] = float(random.randint(0, 1))
            life.ip = (ip + 1) % n

        elif opcode == SENSE_PREY:
            life.registers[0] = float(_sense_prey(life, spatial))
            life.ip = (ip + 1) % n

        elif opcode == SENSE_PREY_DIRECTION:
            dx, dy = _sense_prey_direction(life, spatial, trace_grid)
            life.registers[0] = dx
            life.registers[1] = dy
            life.ip = (ip + 1) % n

        elif opcode == INC_R0:
            life.registers[0] += 1.0
            life.ip = (ip + 1) % n

        elif opcode == DEC_R0:
            life.registers[0] -= 1.0
            life.ip = (ip + 1) % n

        elif opcode == COPY_R0_TO_R1:
            life.registers[1] = life.registers[0]
            life.ip = (ip + 1) % n

        elif opcode == LOAD_R0:
            addr = genome[(ip + 1) % n] % len(life.memory)
            life.registers[0] = life.memory[addr]
            life.ip = (ip + 2) % n

        elif opcode == STORE_R0:
            addr = genome[(ip + 1) % n] % len(life.memory)
            life.memory[addr] = life.registers[0]
            life.ip = (ip + 2) % n

        elif opcode == JUMP:
            target = genome[(ip + 1) % n] % n
            life.ip = target

        elif opcode == JUMP_IF_R0_ZERO:
            target = genome[(ip + 1) % n] % n
            if life.registers[0] == 0.0:
                life.ip = target
            else:
                life.ip = (ip + 2) % n

        elif opcode == JUMP_IF_R0_NZ:
            target = genome[(ip + 1) % n] % n
            if life.registers[0] != 0.0:
                life.ip = target
            else:
                life.ip = (ip + 2) % n

        else:
            life.ip = (ip + 1) % n

        steps += 1