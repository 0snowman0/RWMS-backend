from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RoutineResultSet:

    columns: tuple[str, ...]

    rows: list[
        dict[str, Any]
    ]