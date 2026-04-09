import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import subprocess
import sys
import time
import pygame
import config


class GenesisWindow:
    def __init__(self, size: int = 900) -> None:
        pygame.init()
        pygame.display.set_caption("Genesis")
        self.screen = pygame.display.set_mode((size, size), pygame.RESIZABLE)
        self.world_surface = None
        self.world_width = 0
        self.world_height = 0
        self.species_a = (0, 255, 0)
        self.species_b = (255, 0, 0)
        self.is_dark_mode = self._detect_dark_mode()
        self._apply_theme(self.is_dark_mode)
        self.last_theme_check = 0.0
        self.theme_check_interval = 1.0

    def _detect_dark_mode(self) -> bool:
        if sys.platform != "darwin":
            return False
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0 and result.stdout.strip() == "Dark"
        except Exception:
            return False

    def _apply_theme(self, dark_mode: bool) -> None:
        if dark_mode:
            self.background = (0, 0, 0)
            self.food = (60, 60, 60)
        else:
            self.background = (255, 255, 255)
            self.food = (210, 210, 210)

    def _refresh_theme(self) -> None:
        now = time.time()
        if now - self.last_theme_check < self.theme_check_interval:
            return
        self.last_theme_check = now
        dark_mode = self._detect_dark_mode()
        if dark_mode != self.is_dark_mode:
            self.is_dark_mode = dark_mode
            self._apply_theme(dark_mode)

    def _ensure_world_surface(self, width: int, height: int) -> None:
        if self.world_surface is None or width != self.world_width or height != self.world_height:
            self.world_width = width
            self.world_height = height
            self.world_surface = pygame.Surface((width, height))

    def process_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                side = min(event.w, event.h)
                self.screen = pygame.display.set_mode((side, side), pygame.RESIZABLE)
        return True

    def render(self, life_list, food_grid) -> None:
        self._refresh_theme()

        height = len(food_grid)
        width = len(food_grid[0]) if height > 0 else 0

        if width == 0 or height == 0:
            self.screen.fill(self.background)
            pygame.display.flip()
            return

        self._ensure_world_surface(width, height)
        self.world_surface.fill(self.background)

        for y in range(height):
            row = food_grid[y]
            for x in range(width):
                if row[x] > 0:
                    self.world_surface.set_at((x, y), self.food)

        for organism in life_list:
            if organism.is_dead():
                continue

            x = organism.x
            y = organism.y

            if 0 <= x < width and 0 <= y < height:
                if organism.species_id == config.SPECIES_A:
                    self.world_surface.set_at((x, y), self.species_a)
                elif organism.species_id == config.SPECIES_B:
                    self.world_surface.set_at((x, y), self.species_b)

        window_width, window_height = self.screen.get_size()
        side = min(window_width, window_height)

        if window_width != side or window_height != side:
            self.screen = pygame.display.set_mode((side, side), pygame.RESIZABLE)

        scaled = pygame.transform.scale(self.world_surface, (side, side))

        self.screen.fill(self.background)
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def close(self) -> None:
        pygame.quit()