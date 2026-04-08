import config

FOOD_VALUE = 1
SPECIES_A_VALUE = 2
SPECIES_B_VALUE = 3


def build_frame(life_list, food_grid) -> dict:
    width = config.WORLD_WIDTH
    height = config.WORLD_HEIGHT
    cells = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if food_grid[y][x] > 0:
                cells[y][x] = FOOD_VALUE

    for organism in life_list:
        if organism.is_dead():
            continue

        x = organism.x
        y = organism.y

        if 0 <= x < width and 0 <= y < height:
            if organism.species_id == config.SPECIES_A:
                cells[y][x] = SPECIES_A_VALUE
            elif organism.species_id == config.SPECIES_B:
                cells[y][x] = SPECIES_B_VALUE

    return {
        "width": width,
        "height": height,
        "cells": cells,
    }