"""
백그라운드 스케줄러 — APScheduler로 데이터 자동 수집을 관리한다.

사용 흐름:
1. main.py에서 CollectorScheduler 생성
2. start() 호출 → 즉시 수집 + 주기적 수집 등록
3. 앱 종료 시 stop() 호출
"""
from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.scheduler.tasks import collect_news, collect_laws, collect_support, collect_survey

if TYPE_CHECKING:
    from app.utils.config_loader import AppConfig
    from app.ui.signals import CollectionSignal

logger = logging.getLogger(__name__)


class CollectorScheduler:
    """데이터 자동 수집 스케줄러"""

    def __init__(self, config: AppConfig, signal: CollectionSignal | None = None):
        self._config = config
        self._signal = signal
        self._scheduler = BackgroundScheduler(
            job_defaults={
                "coalesce": True,          # 밀린 작업 1번만 실행
                "max_instances": 1,        # 동시 실행 방지
                "misfire_grace_time": 300,  # 5분 유예
            }
        )
        self._running = False

    def start(self) -> None:
        """스케줄러를 시작하고, 즉시 1회 수집을 트리거한다."""
        if self._running:
            return

        sched_cfg = self._config.scheduler

        # 뉴스 수집 — 매 N분
        self._scheduler.add_job(
            self._job_news,
            trigger=IntervalTrigger(minutes=sched_cfg.news_interval_minutes),
            id="collect_news",
            name="뉴스 RSS 수집",
            replace_existing=True,
        )

        # 법령 수집 — 매 N시간
        self._scheduler.add_job(
            self._job_laws,
            trigger=IntervalTrigger(hours=sched_cfg.law_interval_hours),
            id="collect_laws",
            name="법령 수집",
            replace_existing=True,
        )

        # 지원사업 수집 — 매 N시간
        self._scheduler.add_job(
            self._job_support,
            trigger=IntervalTrigger(hours=sched_cfg.support_interval_hours),
            id="collect_support",
            name="지원사업 수집",
            replace_existing=True,
        )

        # 다문화가족실태조사 통계 — 매 24시간 (법령과 동일 주기)
        self._scheduler.add_job(
            self._job_survey,
            trigger=IntervalTrigger(hours=sched_cfg.law_interval_hours),
            id="collect_survey",
            name="다문화가족실태조사 수집",
            replace_existing=True,
        )

        self._scheduler.start()
        self._running = True
        logger.info(
            "스케줄러 시작 — 뉴스 %d분, 법령 %d시간, 지원사업 %d시간 주기",
            sched_cfg.news_interval_minutes,
            sched_cfg.law_interval_hours,
            sched_cfg.support_interval_hours,
        )

        # 즉시 1회 수집 실행 (백그라운드 스레드에서 — UI 블로킹 방지)
        threading.Thread(target=self.run_once, daemon=True).start()

    # -- 개별 작업 래퍼 (시그널 발행) --------------------------------

    def _job_news(self) -> None:
        try:
            count = collect_news(self._config)
            if self._signal:
                self._signal.news_collected.emit(count)
        except Exception:
            logger.exception("뉴스 수집 실패")
            if self._signal:
                self._signal.error_occurred.emit("뉴스 수집 중 오류 발생")

    def _job_laws(self) -> None:
        try:
            count = collect_laws(self._config)
            if self._signal:
                self._signal.laws_collected.emit(count)
        except Exception:
            logger.exception("법령 수집 실패")
            if self._signal:
                self._signal.error_occurred.emit("법령 수집 중 오류 발생")

    def _job_support(self) -> None:
        try:
            count = collect_support(self._config)
            if self._signal:
                self._signal.support_collected.emit(count)
        except Exception:
            logger.exception("지원사업 수집 실패")
            if self._signal:
                self._signal.error_occurred.emit("지원사업 수집 중 오류 발생")

    def _job_survey(self) -> None:
        try:
            collect_survey(self._config)
        except Exception:
            logger.exception("다문화가족실태조사 수집 실패")
            if self._signal:
                self._signal.error_occurred.emit("다문화가족실태조사 수집 중 오류 발생")

    # ---------------------------------------------------------------

    def run_once(self) -> None:
        """모든 수집을 즉시 1회 실행한다 (시작 시 또는 수동 새로고침 시)."""
        logger.info("즉시 수집 시작...")
        news_count = laws_count = support_count = 0

        try:
            news_count = collect_news(self._config)
        except Exception:
            logger.exception("즉시 뉴스 수집 실패")
        try:
            laws_count = collect_laws(self._config)
        except Exception:
            logger.exception("즉시 법령 수집 실패")
        try:
            support_count = collect_support(self._config)
        except Exception:
            logger.exception("즉시 지원사업 수집 실패")
        try:
            collect_survey(self._config)
        except Exception:
            logger.exception("즉시 다문화가족실태조사 수집 실패")

        logger.info("즉시 수집 완료 — 뉴스 %d, 법령 %d, 지원 %d",
                     news_count, laws_count, support_count)

        if self._signal:
            self._signal.all_collected.emit(news_count, laws_count, support_count)

    def stop(self) -> None:
        """스케줄러를 정지한다."""
        if self._running:
            self._scheduler.shutdown(wait=False)
            self._running = False
            logger.info("스케줄러 종료")

    @property
    def is_running(self) -> bool:
        return self._running
