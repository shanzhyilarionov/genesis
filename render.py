import os
import config

PANEL_WIDTH = 20

def clear_screen() -> None:
    os.system("tput reset")

def print_title() -> None:
    title = f"{config.PROGRAM_NAME} {config.VERSION}"
    print("+ " + "-" * (config.WORLD_WIDTH + PANEL_WIDTH + 3) + " +")
    print("| " + title.center(config.WORLD_WIDTH + PANEL_WIDTH + 3) + " |")

def _fmt_header(label: str, value: str) -> str:
    return f"{label:<11}{value}"

def _fmt_ab(a_val, b_val) -> str:
    return f"A: {str(a_val):<6}  B: {str(b_val):<6}"

def render(world, life_list, food_grid, current_tick: int) -> None:
    clear_screen()
    print_title()
    
    alive = [l for l in life_list if not l.is_dead()]
    alive_A = [l for l in alive if l.species_id == config.SPECIES_A]
    alive_B = [l for l in alive if l.species_id == config.SPECIES_B]
    pop_A = len(alive_A)
    pop_B = len(alive_B)
    total_food_units = sum(sum(row) for row in food_grid)
    config.peak_population_A = max(config.peak_population_A, pop_A)
    config.peak_population_B = max(config.peak_population_B, pop_B)

    for y in range(config.WORLD_HEIGHT):
        for x in range(config.WORLD_WIDTH):
            world[y][x] = " "
    
    for y in range(config.WORLD_HEIGHT):
        for x in range(config.WORLD_WIDTH):
            if food_grid[y][x] > 0:
                world[y][x] = "."
    
    for organism in alive:
        params = config.SPECIES_PARAMETERS[organism.species_id]
        symbol = params["symbol"]
        world[organism.y][organism.x] = symbol

    trait_mutations_A = (
        config.lifespan_mutations_A
        + config.metabolism_mutations_A
        + config.mobility_mutations_A
    )
    
    trait_mutations_B = (
        config.lifespan_mutations_B
        + config.metabolism_mutations_B
        + config.mobility_mutations_B
    )

    total_deaths_A = (
        config.intrinsic_mortality_A
        + config.starvation_mortality_A
        + config.predation_mortality_A
        + config.pollution_mortality_A
    )

    total_deaths_B = (
        config.intrinsic_mortality_B
        + config.starvation_mortality_B
        + config.predation_mortality_B
        + config.pollution_mortality_B
    )

    def _pct(count, total):
        if total <= 0:
            return "0%"
        return f"{int((count / total) * 100)}%"

    panel_lines = []
    panel_lines.append(_fmt_header("Tick:", str(current_tick)))
    panel_lines.append(_fmt_header("Nutrients:", str(total_food_units)))
    panel_lines.append(
        _fmt_header("Pollution:", f"{config.global_pollution_level:.3f}")
    )
    panel_lines.append("")
    panel_lines.append("Population")
    panel_lines.append(_fmt_ab(pop_A, pop_B))
    panel_lines.append("Total Spawned")
    panel_lines.append(_fmt_ab(config.total_spawned_A, config.total_spawned_B))
    panel_lines.append("Peak Population")
    panel_lines.append(_fmt_ab(config.peak_population_A, config.peak_population_B))
    panel_lines.append("Max Generation")
    panel_lines.append(_fmt_ab(config.max_generation_A, config.max_generation_B))
    panel_lines.append("Natality (Tick)")
    panel_lines.append(_fmt_ab(config.birth_A_tick, config.birth_B_tick))
    panel_lines.append("Mortality (Tick)")
    panel_lines.append(_fmt_ab(config.death_A_tick, config.death_B_tick))
    panel_lines.append("Intrinsic Mortality")
    panel_lines.append(
        _fmt_ab(
            _pct(config.intrinsic_mortality_A, total_deaths_A),
            _pct(config.intrinsic_mortality_B, total_deaths_B),
        )
    )
    panel_lines.append("Starvation Mortality")
    panel_lines.append(
        _fmt_ab(
            _pct(config.starvation_mortality_A, total_deaths_A),
            _pct(config.starvation_mortality_B, total_deaths_B),
        )
    )
    panel_lines.append("Predation Mortality")
    panel_lines.append(
        _fmt_ab(
            _pct(config.predation_mortality_A, total_deaths_A),
            _pct(config.predation_mortality_B, total_deaths_B),
        )
    )
    panel_lines.append("Pollution Mortality")
    panel_lines.append(
        _fmt_ab(
            _pct(config.pollution_mortality_A, total_deaths_A),
            _pct(config.pollution_mortality_B, total_deaths_B),
        )
    )
    panel_lines.append("Trait Mutations")
    panel_lines.append(_fmt_ab(trait_mutations_A, trait_mutations_B))
    panel_lines.append("Unique Genomes")
    panel_lines.append(_fmt_ab(config.unique_genomes_A, config.unique_genomes_B))
    panel_lines.append("Genome Diversity")
    panel_lines.append(
        _fmt_ab(
            f"{config.genome_diversity_A:.1f}",
            f"{config.genome_diversity_B:.1f}",
        )
    )
    panel_lines.append("Mean Instruction")
    panel_lines.append("Sequence Length")
    panel_lines.append(
        _fmt_ab(
            f"{config.mean_exec_length_A:.1f}",
            f"{config.mean_exec_length_B:.1f}",
        )
    )
    panel_lines.append("Dominant Opcode")
    panel_lines.append(_fmt_ab(config.dominant_opcode_A, config.dominant_opcode_B))
    panel_lines.append("VM Idle Rate")
    panel_lines.append(
        _fmt_ab(
            f"{int(config.vm_idle_rate_A * 100):d}%",
            f"{int(config.vm_idle_rate_B * 100):d}%",
        )
    )
    
    top_border = "+ " + "-" * PANEL_WIDTH + " + " + "-" * config.WORLD_WIDTH + " +"
    print(top_border)

    for y in range(config.WORLD_HEIGHT):
        panel_text = panel_lines[y] if y < len(panel_lines) else ""
        panel_text = f"{panel_text:<{PANEL_WIDTH}}"
        panel_segment = f"| {panel_text} |"
        map_row = "".join(world[y])
        map_segment = f" {map_row} |"
        print(panel_segment + map_segment)

    print(top_border)