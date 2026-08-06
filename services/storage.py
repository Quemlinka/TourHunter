from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from models.tour import Tour


class TourStorage:
    def __init__(self, path: str | Path = "data/last_tour.json") -> None:
        self.path = Path(path)

    def load(self) -> Tour | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return Tour(**data)
        except (OSError, ValueError, TypeError):
            return None

    def save(self, tour: Tour) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(asdict(tour), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(self.path)
