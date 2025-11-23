import config
from genome import init_random_genome

class Life:
    _id_counter = 0

    def __init__(
        self,
        x: int,
        y: int,
        energy: float,
        lifespan: int,
        metabolism: float,
        mobility: float,
        generation: int,
        species_id: int,
    ) -> None:
        self.id = Life._id_counter
        Life._id_counter += 1
        self.x = x
        self.y = y
        self.energy = float(energy)
        self.age_ticks = 0
        self.lifespan_ticks = lifespan
        self.metabolism_rate = metabolism
        self.mobility_probability = mobility
        self.generation_index = generation
        self.species_id = species_id
        self.has_lineage_mutated = False
        self.died_from_pollution = False
        self.died_from_predation = False
        self.genome: list[int] = init_random_genome()
        self.ip: int = 0
        self.registers: list[float] = [0.0, 0.0, 0.0, 0.0]
        self.memory: list[float] = [0.0] * 16

    def is_dead(self) -> bool:
        return self.energy <= 0.0 or self.age_ticks > self.lifespan_ticks