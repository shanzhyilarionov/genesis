import random

import config
from core.life import Life
from genetics.genome import mutate_genome
from genetics.spatial_index import SpatialIndex


def _move_random(life: Life, spatial: SpatialIndex) -> None:
    dx, dy = random.choice([
        (1, 0), (-1, 0),
        (0, 1), (0, -1),
        (0, 0),
    ])
    old_x, old_y = life.x, life.y
    nx = max(0, min(config.WORLD_WIDTH - 1, life.x + dx))
    ny = max(0, min(config.WORLD_HEIGHT - 1, life.y + dy))
    life.x, life.y = nx, ny
    spatial.move(life, old_x, old_y, nx, ny)


def _move_to_food(life: Life, food_grid, spatial: SpatialIndex) -> None:
    if life.species_id != config.SPECIES_A:
        return

    vision_range = 2
    best_score = -1e9
    best_positions = []

    for dx in range(-vision_range, vision_range + 1):
        for dy in range(-vision_range, vision_range + 1):
            nx = max(0, min(config.WORLD_WIDTH - 1, life.x + dx))
            ny = max(0, min(config.WORLD_HEIGHT - 1, life.y + dy))
            score = food_grid[ny][nx]

            if score > best_score:
                best_score = score
                best_positions = [(nx, ny)]
            elif score == best_score:
                best_positions.append((nx, ny))

    if best_positions:
        old_x, old_y = life.x, life.y
        nx, ny = random.choice(best_positions)
        life.x, life.y = nx, ny
        spatial.move(life, old_x, old_y, nx, ny)


def _predator_candidate_moves():
    return [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]


def _bounded_step(x: int, y: int, dx: int, dy: int) -> tuple[int, int]:
    nx = max(0, min(config.WORLD_WIDTH - 1, x + dx))
    ny = max(0, min(config.WORLD_HEIGHT - 1, y + dy))
    return nx, ny


def _local_prey_score(spatial: SpatialIndex, x: int, y: int) -> float:
    vision_range = config.PREDATOR_SEARCH_RADIUS

    bx0 = max(0, (x - vision_range) // spatial.bucket_size)
    bx1 = (x + vision_range) // spatial.bucket_size
    by0 = max(0, (y - vision_range) // spatial.bucket_size)
    by1 = (y + vision_range) // spatial.bucket_size

    best_score = 0.0

    for by in range(by0, by1 + 1):
        for bx in range(bx0, bx1 + 1):
            for prey in spatial.prey_buckets.get((bx, by), []):
                if prey.is_dead():
                    continue

                dx = abs(prey.x - x)
                dy = abs(prey.y - y)

                if dx > vision_range or dy > vision_range:
                    continue

                dist = dx + dy

                if dist == 0:
                    return 100.0

                score = config.PREDATOR_PREY_WEIGHT / (dist + 1.0)
                if score > best_score:
                    best_score = score

    return best_score


def _score_predator_cell(life: Life, spatial: SpatialIndex, trace_grid, nx: int, ny: int) -> float:
    score = _local_prey_score(spatial, nx, ny)

    score += trace_grid[ny][nx] * config.PREDATOR_TRACE_BONUS

    if (nx, ny) == (life.last_x, life.last_y):
        score -= config.PREDATOR_REVISIT_PENALTY

    score += random.uniform(
        -config.PREDATOR_RANDOM_NOISE,
        config.PREDATOR_RANDOM_NOISE,
    )

    return score


def _move_towards_prey(life: Life, spatial: SpatialIndex, trace_grid) -> None:
    if life.species_id != config.SPECIES_B:
        return

    dx = int(round(life.registers[0]))
    dy = int(round(life.registers[1]))

    if dx == 0 and dy == 0 and life.current_search_score >= 50.0:
        trace_grid[life.y][life.x] += config.PREDATOR_TRACE_DEPOSIT
        life.last_search_score = life.current_search_score
        return

    if life.current_search_score > life.last_search_score:
        life.run_ticks_left = min(life.run_ticks_left + config.PREDATOR_RUN_BONUS, 4)
    else:
        life.run_ticks_left = max(0, life.run_ticks_left - 1)

        if random.random() < config.PREDATOR_TUMBLE_PROB:
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    if dx == 0 and dy == 0:
        dx, dy = life.heading_dx, life.heading_dy

    if dx == 0 and dy == 0:
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    old_x, old_y = life.x, life.y
    life.last_x, life.last_y = old_x, old_y

    nx, ny = _bounded_step(life.x, life.y, dx, dy)

    life.x, life.y = nx, ny
    life.heading_dx, life.heading_dy = dx, dy

    spatial.move(life, old_x, old_y, nx, ny)

    if life.current_search_score > life.last_search_score:
        trace_grid[ny][nx] += config.PREDATOR_TRACE_DEPOSIT

    life.last_search_score = life.current_search_score


def _eat_plant(life: Life, food_grid) -> None:
    if life.species_id != config.SPECIES_A:
        return

    cell_amount = food_grid[life.y][life.x]
    if cell_amount <= 0:
        return

    consumed = min(config.FOOD_CONSUMPTION_PER_EVENT, cell_amount)
    food_grid[life.y][life.x] -= consumed
    life.energy += consumed * config.FOOD_TO_ENERGY_FACTOR


def _sense_food(life: Life, food_grid) -> int:
    if life.species_id != config.SPECIES_A:
        return 0
    return 1 if food_grid[life.y][life.x] > 0 else 0


def _sense_neighbor(life: Life, spatial: SpatialIndex) -> int:
    return 1 if spatial.alive_same_cell_count(life.x, life.y) > 1 else 0


def _sense_prey(life: Life, spatial: SpatialIndex) -> int:
    if life.species_id != config.SPECIES_B:
        return 0

    vision_range = 100
    return 1 if spatial.prey_exists_in_range(life.x, life.y, vision_range) else 0


def _sense_prey_direction(life: Life, spatial: SpatialIndex, trace_grid) -> tuple[float, float]:
    if life.species_id != config.SPECIES_B:
        return 0.0, 0.0

    vision_range = config.PREDATOR_SEARCH_RADIUS

    if not spatial.prey_exists_in_range(life.x, life.y, vision_range):
        dx = life.heading_dx
        dy = life.heading_dy

        if dx == 0 and dy == 0:
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        life.current_search_score = trace_grid[life.y][life.x] * config.PREDATOR_TRACE_BONUS
        return float(dx), float(dy)

    best_score = -1e18
    best_dirs = []

    for dx, dy in _predator_candidate_moves():
        nx, ny = _bounded_step(life.x, life.y, dx, dy)
        score = _score_predator_cell(life, spatial, trace_grid, nx, ny)

        if (
            dx == life.heading_dx
            and dy == life.heading_dy
            and life.run_ticks_left > 0
        ):
            score += config.PREDATOR_HEADING_BONUS

        if score > best_score:
            best_score = score
            best_dirs = [(dx, dy)]
        elif score == best_score:
            best_dirs.append((dx, dy))

    chosen_dx, chosen_dy = random.choice(best_dirs)
    life.current_search_score = best_score

    return float(chosen_dx), float(chosen_dy)


def _try_reproduce(life: Life, offspring_list: list[Life], spatial: SpatialIndex) -> None:
    params = config.SPECIES_PARAMETERS[life.species_id]
    threshold = params["reproduction_threshold"]
    cost = params["reproduction_cost"]
    probability = params["reproduction_probability"]

    if life.energy < threshold:
        return
    if random.random() > probability:
        return

    life.energy -= cost
    if life.energy <= 0.0:
        return

    dx, dy = random.choice([
        (1, 0), (-1, 0),
        (0, 1), (0, -1),
        (0, 0),
    ])
    child_x = max(0, min(config.WORLD_WIDTH - 1, life.x + dx))
    child_y = max(0, min(config.WORLD_HEIGHT - 1, life.y + dy))
    species_id = life.species_id

    if random.random() < config.MUTATION_PROBABILITY:
        delta_lifespan = random.randint(-4, 4)
    else:
        delta_lifespan = 0

    min_life = params["lifespan_min"]
    max_life = params["lifespan_max"]
    child_lifespan = max(
        min_life,
        min(max_life, life.lifespan_ticks + delta_lifespan),
    )

    if random.random() < config.MUTATION_PROBABILITY:
        delta_metabolism = random.uniform(-0.1, 0.1)
    else:
        delta_metabolism = 0.0

    min_meta = params["metabolism_min"]
    max_meta = params["metabolism_max"]
    child_metabolism = max(
        min_meta,
        min(max_meta, life.metabolism_rate + delta_metabolism),
    )

    if random.random() < config.MUTATION_PROBABILITY:
        delta_mobility = random.uniform(-0.05, 0.05)
    else:
        delta_mobility = 0.0

    min_move = params["mobility_min"]
    max_move = params["mobility_max"]
    child_mobility = max(
        min_move,
        min(max_move, life.mobility_probability + delta_mobility),
    )

    child_energy = random.randint(
        params["energy_min"],
        params["energy_max"],
    )
    child_generation = life.generation_index + 1

    child = Life(
        child_x,
        child_y,
        child_energy,
        child_lifespan,
        child_metabolism,
        child_mobility,
        child_generation,
        species_id=species_id,
    )
    child.genome = mutate_genome(life.genome)
    child.ip = 0
    child.registers = [0.0, 0.0, 0.0, 0.0]
    child.memory = [0.0] * len(life.memory)
    offspring_list.append(child)
    spatial.add(child)