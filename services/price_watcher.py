from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol
from models.tour import Tour
from parsers.travelata_api import TravelataAPI
from parsers.coral_api import CoralAPI
from services.storage import TourStorage
from tour_config import PRICE_LIMIT


logger = logging.getLogger(__name__)

@dataclass(frozen=True, slots=True)
class CheckResult:
    tour: Tour | None
    should_notify: bool
    previous_tour: Tour | None


class TourSource(Protocol):
    def get_best_tour(self) -> Tour | None:
        ...


class PriceWatcher:

    def __init__(
        self,
        api: TravelataAPI | None = None,
        storage: TourStorage | None = None,
        sources: tuple[TourSource, ...] | None = None,
    ) -> None:

        self.sources = (
           api or TravelataAPI(),
           CoralAPI(),
        )

        self.storage = storage or TourStorage()

    def check_prices(self) -> CheckResult:

        logger.info("=" * 60)
        logger.info("НАЧИНАЮ ПРОВЕРКУ ЦЕН")

        previous = self.storage.load()

        logger.info("Предыдущий тур: %s", previous)

        candidates: list[Tour] = []

        for source in self.sources:

            logger.info(
                "Источник: %s",
                type(source).__name__,
            )

            try:
                candidate = source.get_best_tour()

            except Exception:
                logger.exception(
                    "Ошибка источника %s",
                    type(source).__name__,
                )
                continue

            if candidate is None:

                logger.info("Туры не найдены")

                continue

            logger.info(
                "Лучший тур: %s ₽ | %s | %s ночей",
                f"{candidate.price:,}".replace(",", " "),
                candidate.checkin_date,
                candidate.tour_nights,
            )

            candidates.append(candidate)

        current = min(
            candidates,
            key=lambda tour: tour.price,
            default=None,
        )

        if current is None:

            logger.warning("Не найдено ни одного тура")

            return CheckResult(
                tour=None,
                should_notify=False,
                previous_tour=previous,
            )

        notify = self._should_notify(
            previous,
            current,
        )

        logger.info(
            "Итог: %s ₽",
            f"{current.price:,}".replace(",", " "),
        )

        logger.info(
            "Отправлять уведомление: %s",
            notify,
        )

        self.storage.save(current)

        return CheckResult(
            tour=current,
            should_notify=notify,
            previous_tour=previous,
        )

    @staticmethod
    def _should_notify(
        previous: Tour | None,
        current: Tour,
    ) -> bool:

        if current.price > PRICE_LIMIT:

            logger.info(
                "Цена выше лимита (%s ₽)",
                PRICE_LIMIT,
            )

            return False

        if previous is None:

            logger.info(
                "Первый запуск — отправляю найденный тур"
            )

            return True

        if (
            current.identity == previous.identity
            and current.price == previous.price
        ):

            logger.info(
                "Цена не изменилась"
            )

            return False

        if current.price < previous.price:

            logger.info(
                "Цена снизилась"
            )

            return True

        if (
            current.identity != previous.identity
            and current.price <= previous.price
        ):

            logger.info(
                "Найден другой тур не дороже предыдущего"
            )

            return True

        logger.info(
            "Изменений нет"
        )

        return False