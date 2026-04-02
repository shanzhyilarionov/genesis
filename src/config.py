WORLD_WIDTH = 200
WORLD_HEIGHT = 120

MAX_FOOD_UNITS = 10
FOOD_REGEN_PROBABILITY = 0.005
FOOD_DECAY_PROBABILITY = 0.005
FOOD_REGEN_INCREMENT = 1
FOOD_DECAY_DECREMENT = 1
FOOD_CONSUMPTION_PER_EVENT = 1
FOOD_TO_ENERGY_FACTOR = 2

SPECIES_A = 1
SPECIES_B = 2

INITIAL_POPULATION_A = 10
INITIAL_POPULATION_B = 5

PREDATION_ENERGY_GAIN_B = 10

SPECIES_PARAMETERS = {
    SPECIES_A: {
        "name": "Species A",
        "lifespan_min": 30,
        "lifespan_max": 80,
        "energy_min": 10,
        "energy_max": 20,
        "metabolism_min": 0.05,
        "metabolism_max": 0.15,
        "mobility_min": 0.6,
        "mobility_max": 0.8,
        "reproduction_threshold": 20,
        "reproduction_cost": 10,
        "reproduction_probability": 0.8,
    },
    SPECIES_B: {
        "name": "Species B",
        "lifespan_min": 40,
        "lifespan_max": 120,
        "energy_min": 20,
        "energy_max": 30,
        "metabolism_min": 0.1,
        "metabolism_max": 0.2,
        "mobility_min": 0.7,
        "mobility_max": 0.9,
        "reproduction_threshold": 30,
        "reproduction_cost": 15,
        "reproduction_probability": 0.6,
    },
}

MUTATION_PROBABILITY = 0.0004

POLLUTION_INCREMENT_PER_LIFE = 0.00001
POLLUTION_CAP = 1.0
global_pollution_level = 0.0

TICK_DELAY_SECONDS = 0.2
MAX_TICK_COUNT = 1000

PREDATOR_SEARCH_RADIUS = 20
PREDATOR_TRACE_DECAY = 0.9
PREDATOR_TRACE_DEPOSIT = 1.5
PREDATOR_TRACE_BONUS = 0.3
PREDATOR_PREY_WEIGHT = 5
PREDATOR_REVISIT_PENALTY = 0.8
PREDATOR_TUMBLE_PROB = 0.5
PREDATOR_RANDOM_NOISE = 0.1
PREDATOR_RUN_BONUS = 2
PREDATOR_HEADING_BONUS = 0.25