PROGRAM_NAME = "GENESIS"
VERSION = "v1.0.0"

WORLD_WIDTH = 77
WORLD_HEIGHT = 39

MAX_FOOD_UNITS = 10
FOOD_REGEN_PROBABILITY = 0.005
FOOD_DECAY_PROBABILITY = 0.005
FOOD_REGEN_INCREMENT = 1
FOOD_DECAY_DECREMENT = 1
FOOD_CONSUMPTION_PER_EVENT = 1
FOOD_TO_ENERGY_FACTOR = 2

SPECIES_A = 1
SPECIES_B = 2

INITIAL_POPULATION_A = 5
INITIAL_POPULATION_B = 2

PREDATION_ENERGY_GAIN_B = 10

SPECIES_PARAMETERS = {
    SPECIES_A: {
        "name": "Species A",
        "symbol": "*",
        "lifespan_min": 30,
        "lifespan_max": 80,
        "energy_min": 10,
        "energy_max": 20,
        "metabolism_min": 0.05,
        "metabolism_max": 0.15,
        "mobility_min": 0.6,
        "mobility_max": 0.9,
        "reproduction_threshold": 20,
        "reproduction_cost": 6,
        "reproduction_probability": 0.8,
    },
    SPECIES_B: {
        "name": "Species B",
        "symbol": "@",
        "lifespan_min": 40,
        "lifespan_max": 120,
        "energy_min": 20,
        "energy_max": 30,
        "metabolism_min": 0.25,
        "metabolism_max": 0.5,
        "mobility_min": 0.85,
        "mobility_max": 0.95,
        "reproduction_threshold": 30,
        "reproduction_cost": 20,
        "reproduction_probability": 0.5,
    },
}

MUTATION_PROBABILITY = 0.0004

mutated_individuals_A = 0
mutated_individuals_B = 0

lifespan_mutations_A = 0
lifespan_mutations_B = 0

metabolism_mutations_A = 0
metabolism_mutations_B = 0

mobility_mutations_A = 0
mobility_mutations_B = 0

POLLUTION_INCREMENT_PER_LIFE = 0.00001
POLLUTION_CAP = 1.0
global_pollution_level = 0.0

total_spawned_A = 0
total_spawned_B = 0

peak_population_A = 0
peak_population_B = 0

max_generation_A = 0
max_generation_B = 0

birth_A_tick = 0
birth_B_tick = 0
death_A_tick = 0
death_B_tick = 0

intrinsic_mortality_A = 0
starvation_mortality_A = 0
pollution_mortality_A = 0
predation_mortality_A = 0

intrinsic_mortality_B = 0
starvation_mortality_B = 0
pollution_mortality_B = 0
predation_mortality_B = 0

unique_genomes_A = 0
unique_genomes_B = 0
genome_diversity_A = 0.0
genome_diversity_B = 0.0

vm_idle_rate_A = 0.0
vm_idle_rate_B = 0.0
dominant_opcode_A = 0
dominant_opcode_B = 0
mean_exec_length_A = 0.0
mean_exec_length_B = 0.0

TICK_DELAY_SECONDS = 0.25
MAX_TICK_COUNT = 600