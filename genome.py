import random

MAX_OPCODE = 32

def init_random_genome(length: int = 32) -> list[int]:
    return [random.randint(0, MAX_OPCODE) for _ in range(length)]

def mutate_genome(genome: list[int], mutation_rate: float = 0.05) -> list[int]:
    new_genome = genome[:]
    for i in range(len(new_genome)):
        if random.random() < mutation_rate:
            new_genome[i] = random.randint(0, MAX_OPCODE)
    return new_genome