"""
다문화가족실태조사 통계 수집 서비스

성평등가족부 전국다문화가족실태조사 통계 데이터 정보 서비스 (data.go.kr #15078218)
- 조사 연도 목록: getServeyMulticulturalFamliyYearList
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

import requests
from sqlalchemy import select

from app.models.database import get_session
from app.models.survey import SurveyStats

if TYPE_CHECKING:
    from app.utils.config_loader import AppConfig

logger = logging.getLogger(__name__)


class SurveyService:
    """다문화가족실태조사 통계 API 수집기"""

    BASE_URL = (
        "http://apis.data.go.kr/1383000/stis"
        "/srvyMltCltrFmlyTblDataService"
    )

    def __init__(self, config: AppConfig):
        self._config = config
        self._api_key = config.multicultural_survey_api_key
        self._timeout = 20

    def fetch_all(self) -> int:
        """조사 연도 목록을 수집한다. 새로 저장된 건수를 반환."""
        if not self._api_key:
            logger.warning("다문화가족실태조사 API 키 미설정 — 수집 건너뜀")
            return 0

        total = 0
        try:
            total += self._fetch_year_list()
        except Exception:
            logger.exception("다문화가족실태조사 수집 실패")

        return total

    def _fetch_year_list(self) -> int:
        """조사 연도 목록을 조회한다."""
        url = f"{self.BASE_URL}/getServeyMulticulturalFamliyYearList"

        params = {
            "serviceKey": self._api_key,
            "numOfRows": 50,
            "pageNo": 1,
            "type": "json",
        }

        try:
            resp = requests.get(url, params=params, timeout=self._timeout)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as e:
            logger.warning("다문화가족실태조사 API 요청 실패: %s", e)
            return 0

        # 응답 구조: response > body > items > item
        body = data.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])

        if not items:
            logger.info("다문화가족실태조사 조회 결과 없음")
            return 0

        return self._save_items(items)

    def _save_items(self, items: list[dict]) -> int:
        """조회된 항목을 DB에 저장한다."""
        saved = 0
        session_gen = get_session()
        session = next(session_gen)
        try:
            for item in items:
                approval_no = item.get("aprvStatsNo", "")
                survey_year = item.get("statsTimeNm", "")

                if not survey_year:
                    continue

                # 중복 확인
                exists = session.execute(
                    select(SurveyStats.id).where(
                        SurveyStats.approval_no == approval_no,
                        SurveyStats.survey_year == survey_year,
                    )
                ).scalar_one_or_none()
                if exists:
                    continue

                stats = SurveyStats(
                    approval_no=approval_no,
                    survey_name=item.get("statsExmnNm", ""),
                    cycle=item.get("statsCyclDvsnNm", ""),
                    survey_year=survey_year,
                    data_created=item.get("dataCrtrYmd", ""),
                    fetched_at=datetime.now(),
                )
                session.add(stats)
                saved += 1

            session.commit()
            if saved:
                logger.info("다문화가족실태조사 %d건 신규 저장", saved)
        except Exception:
            session.rollback()
            raise
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

        return saved
