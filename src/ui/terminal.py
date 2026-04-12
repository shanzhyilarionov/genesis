import sys

CELL_WIDTH = 24
GAP = "  "


def _value_text(value) -> str:
    if value is None:
        return "N/A"
    return str(value)


def _float_text(value, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


def _percent_text(part: int | None, total: int | None) -> str:
    if part is None or total is None or total == 0:
        return "N/A"
    return f"{round(part * 100 / total)}%"


def _cell(label: str, value: str, width: int = CELL_WIDTH) -> str:
    name = f"{label}: "
    return name + value.rjust(width - len(name))


def _pair(
    left_label: str,
    left_value: str,
    right_label: str,
    right_value: str,
) -> str:
    return _cell(left_label, left_value) + GAP + _cell(right_label, right_value)


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

        death_a = getattr(snapshot, "death_a", None)
        death_b = getattr(snapshot, "death_b", None)

        intrinsic_death_a = getattr(snapshot, "intrinsic_death_a", None)
        intrinsic_death_b = getattr(snapshot, "intrinsic_death_b", None)

        starvation_death_a = getattr(snapshot, "starvation_death_a", None)
        starvation_death_b = getattr(snapshot, "starvation_death_b", None)

        predation_death_a = getattr(snapshot, "predation_death_a", None)
        pollution_death_a = getattr(snapshot, "pollution_death_a", None)
        pollution_death_b = getattr(snapshot, "pollution_death_b", None)

        lines = [
            _cell("Tick", _value_text(getattr(snapshot, "tick", None))),
            _cell("Food", _value_text(getattr(snapshot, "food_total", None))),
            _cell("Pollution", _float_text(getattr(snapshot, "pollution", None), 4)),
            "",
            _pair(
                "Population A",
                _value_text(getattr(snapshot, "population_a", None)),
                "Population B",
                _value_text(getattr(snapshot, "population_b", None)),
            ),
            _pair(
                "Birth A",
                _value_text(getattr(snapshot, "birth_a", None)),
                "Birth B",
                _value_text(getattr(snapshot, "birth_b", None)),
            ),
            _pair(
                "Death A",
                _value_text(death_a),
                "Death B",
                _value_text(death_b),
            ),
            _pair(
                "Mean Age A",
                _float_text(getattr(snapshot, "avg_age_a", None), 2),
                "Mean Age B",
                _float_text(getattr(snapshot, "avg_age_b", None), 2),
            ),
            _pair(
                "Mean Energy A",
                _float_text(getattr(snapshot, "avg_energy_a", None), 2),
                "Mean Energy B",
                _float_text(getattr(snapshot, "avg_energy_b", None), 2),
            ),
            _pair(
                "Mean Metabolism A",
                _float_text(getattr(snapshot, "avg_metabolism_a", None), 2),
                "Mean Metabolism B",
                _float_text(getattr(snapshot, "avg_metabolism_b", None), 2),
            ),
            _pair(
                "Intrinsic Death A",
                _percent_text(intrinsic_death_a, death_a),
                "Intrinsic Death B",
                _percent_text(intrinsic_death_b, death_b),
            ),
            _pair(
                "Starvation Death A",
                _percent_text(starvation_death_a, death_a),
                "Starvation Death B",
                _percent_text(starvation_death_b, death_b),
            ),
            _pair(
                "Predation Death A",
                _percent_text(predation_death_a, death_a),
                "Pollution Death B",
                _percent_text(pollution_death_b, death_b),
            ),
            _pair(
                "Pollution Death A",
                _percent_text(pollution_death_a, death_a),
                "Mutations B",
                _value_text(getattr(snapshot, "mutations_b", None)),
            ),
            _pair(
                "Mutations A",
                _value_text(getattr(snapshot, "mutations_a", None)),
                "Dominant Opcode B",
                _value_text(getattr(snapshot, "dominant_opcode_b", None)),
            ),
            _cell(
                "Dominant Opcode A",
                _value_text(getattr(snapshot, "dominant_opcode_a", None)),
            ),
            "",
        ]

        output = "\n".join(lines)
        sys.stdout.write("\x1b[H\x1b[J")
        sys.stdout.write(output)
        sys.stdout.flush()