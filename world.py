import random
import config

def create_initial_food_grid():
    return [
        [
            random.randint(3, 6) if random.random() < 0.6 else 0
            for _ in range(config.WORLD_WIDTH)
        ]
        for _ in range(config.WORLD_HEIGHT)
    ]

def regenerate_food(food_grid) -> None:
    pollution_factor = max(0.0, 1.0 - config.global_pollution_level)

    for y in range(config.WORLD_HEIGHT):
        for x in range(config.WORLD_WIDTH):
            amount = food_grid[y][x]

            if 0 < amount < config.MAX_FOOD_UNITS:
                if random.random() < config.FOOD_REGEN_PROBABILITY * pollution_factor:
                    food_grid[y][x] = min(
                        config.MAX_FOOD_UNITS,
                        amount + config.FOOD_REGEN_INCREMENT,
                    )
            
            if amount > 0 and random.random() < config.FOOD_DECAY_PROBABILITY:
                new_amount = amount - config.FOOD_DECAY_DECREMENT
                food_grid[y][x] = max(0, new_amount)
            
            if food_grid[y][x] == 0 and random.random() < 0.001 * pollution_factor:
                food_grid[y][x] = 1