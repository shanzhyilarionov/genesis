import sys

LABEL_WIDTH = 15

def _row(label: str, value: str) -> str:
    return f"{label:<{LABEL_WIDTH}}{value}"

class TerminalStatsPanel:
    def __init__(self) -> None:
        self._active = False

    def enter(self) -> None:
        if self._active:
            return
        sys.stdout.write("\x1b[?1049h")
        sys.stdout.write("\x1b[2J\x1b[H")
        sys.stdout.flush()
        self._active = True

    def leave(self) -> None:
        if not self._active:
            return
        sys.stdout.write("\x1b[?1049l")
        sys.stdout.flush()
        self._active = False

    def render(self, snapshot) -> None:
        if not self._active:
            self.enter()

        sys.stdout.write("\x1b[H\x1b[J")

        lines = [
            _row("Tick:", str(snapshot.tick)),
            _row("Food:", str(snapshot.food_total)),
            _row("Pollution:", f"{snapshot.pollution:.3f}"),
            _row("Population A:", str(snapshot.population_a)),
            _row("Population B:", str(snapshot.population_b)),
            _row("Mean Age A:", f"{snapshot.avg_age_a:.2f}"),
            _row("Mean Age B:", f"{snapshot.avg_age_b:.2f}"),
            _row("Mean Energy A:", f"{snapshot.avg_energy_a:.2f}"),
            _row("Mean Energy B:", f"{snapshot.avg_energy_b:.2f}"),
            "",
        ]

        sys.stdout.write("\n".join(lines))
        sys.stdout.flush()