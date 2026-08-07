from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path

from models.tour import Tour


logger = logging.getLogger(__name__)


class TourStorage:

    def __init__(
        self,
        path: str | Path = "data/last_tour.json",
    ) -> None:

        self.path = Path(path)

    def load(self) -> Tour | None:

        if not self.path.exists():

            logger.info(
                "Файл last_tour.json отсутствует"
            )

            return None

        try:

            data = json.loads(
                self.path.read_text(
                    encoding="utf-8",
                )
            )

            tour = Tour(**data)

            logger.info(
                "Загружен предыдущий тур: %s ₽ (%s)",
                tour.price,
                tour.checkin_date,
            )

            return tour

        except Exception:

            logger.exception(
                "Не удалось загрузить last_tour.json"
            )

            return None

    def save(
        self,
        tour: Tour,
    ) -> None:

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = self.path.with_suffix(
            ".tmp"
        )

        temp.write_text(
            json.dumps(
                asdict(tour),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temp.replace(self.path)

        logger.info(
            "Сохранён новый минимум: %s ₽ (%s)",
            tour.price,
            tour.checkin_date,
        )