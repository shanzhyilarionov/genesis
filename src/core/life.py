from genetics.genome import init_random_genome

class Life:
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
        genome: list[int] | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.energy = float(energy)
        self.age_ticks = 0
        self.lifespan_ticks = lifespan
        self.metabolism_rate = metabolism
        self.mobility_probability = mobility
        self.generation_index = generation
        self.species_id = species_id
        self.genome: list[int] = genome if genome is not None else init_random_genome()
        self.ip: int = 0
        self.registers: list[float] = [0.0, 0.0, 0.0, 0.0]
        self.memory: list[float] = [0.0] * 16
        self.heading_dx: int = 0
        self.heading_dy: int = 0
        self.last_search_score: float = 0.0
        self.current_search_score: float = 0.0
        self.run_ticks_left: int = 0
        self.last_x: int = x
        self.last_y: int = y

    def is_dead(self) -> bool:
        return self.energy <= 0.0 or self.age_ticks > self.lifespan_ticks