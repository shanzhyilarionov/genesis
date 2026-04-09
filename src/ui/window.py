import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import re
import shutil
import subprocess
import sys
import time
import pygame
import config
from typing import Optional


class GenesisWindow:
    def __init__(self, size: int = 500) -> None:
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
        if sys.platform == "darwin":
            return self._detect_dark_mode_macos()
        if sys.platform == "win32":
            return self._detect_dark_mode_windows()
        if sys.platform.startswith("linux"):
            return self._detect_dark_mode_linux()
        return False

    def _detect_dark_mode_macos(self) -> bool:
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                check=False,
                timeout=1,
            )
            return result.returncode == 0 and result.stdout.strip() == "Dark"
        except Exception:
            return False

    def _detect_dark_mode_windows(self) -> bool:
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")

            return int(value) == 0
        except Exception:
            return False

    def _detect_dark_mode_linux(self) -> bool:
        portal_value = self._detect_dark_mode_linux_portal()
        if portal_value is not None:
            return portal_value

        gsettings_value = self._detect_dark_mode_linux_gsettings()
        if gsettings_value is not None:
            return gsettings_value

        return False

    def _detect_dark_mode_linux_portal(self) -> Optional[bool]:
        if not shutil.which("gdbus"):
            return None

        try:
            result = subprocess.run(
                [
                    "gdbus",
                    "call",
                    "--session",
                    "--dest",
                    "org.freedesktop.portal.Desktop",
                    "--object-path",
                    "/org/freedesktop/portal/desktop",
                    "--method",
                    "org.freedesktop.portal.Settings.ReadOne",
                    "org.freedesktop.appearance",
                    "color-scheme",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=1,
            )

            if result.returncode != 0:
                return None

            text = result.stdout.strip()
            match = re.search(r"\b(?:uint32\s+)?([012])\b", text)
            if not match:
                return None

            value = int(match.group(1))
            if value == 1:
                return True
            if value == 2:
                return False
            return False
        except Exception:
            return None

    def _detect_dark_mode_linux_gsettings(self) -> Optional[bool]:
        if not shutil.which("gsettings"):
            return None

        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True,
                text=True,
                check=False,
                timeout=1,
            )

            if result.returncode == 0:
                value = result.stdout.strip().strip("'").lower()
                if value in {"prefer-dark", "dark"}:
                    return True
                if value in {"prefer-light", "light", "default"}:
                    return False

            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True,
                text=True,
                check=False,
                timeout=1,
            )

            if result.returncode == 0:
                value = result.stdout.strip().strip("'").lower()
                if "-dark" in value or value.endswith(":dark"):
                    return True
                return False
        except Exception:
            return None

        return None

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