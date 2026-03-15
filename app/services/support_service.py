"""
지원사업 수집 서비스 — 공공데이터포털 API에서 다문화 관련 지원사업을 수집한다.

공공데이터포털: https://www.data.go.kr
- 다문화가족지원 관련 서비스 목록 조회
- 정부24 보조금24 API 등 활용
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING

import requests
from sqlalchemy import select

from app.models.database import get_session
from app.models.support import SupportProgram

if TYPE_CHECKING:
    from app.utils.config_loader import AppConfig

logger = logging.getLogger(__name__)


class SupportService:
    """공공데이터포털 기반 지원사업 수집기"""

    # 공공데이터포털 다문화 관련 서비스 API
    BASE_URL = "https://api.odcloud.kr/api"

    def __init__(self, config: AppConfig):
        self._config = config
        self._api_key = config.public_data_api_key
        self._timeout = 20

    def fetch_all(self) -> int:
        """지원사업 정보를 수집한다. 새로 저장된 건수를 반환."""
        if not self._api_key:
            logger.warning("공공데이터포털 API 키 미설정 — 지원사업 수집 건너뜀")
            return 0

        total = 0
        try:
            total += self._fetch_multicultural_support()
        except Exception:
            logger.exception("지원사업 수집 실패")

        return total

    def _fetch_multicultural_support(self) -> int:
        """다문화가족 지원사업 목록을 조회한다."""
        # 보조금24 또는 다문화 관련 공공데이터 API
        # 실제 API 엔드포인트는 승인된 서비스에 따라 달라짐
        # 여기서는 범용 구조를 제공하고, 실제 URL은 사용자의 승인 서비스에 맞게 조정
        url = f"{self.BASE_URL}/15083415/v1/uddi:25844710-a56d-49ef-8aff-0a3e8e56c97c"

        params = {
            "page": 1,
            "perPage": 50,
            "serviceKey": self._api_key,
        }

        try:
            resp = requests.get(url, params=params, timeout=self._timeout)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as e:
            logger.warning("공공데이터포털 요청 실패: %s", e)
            return 0

        items = data.get("data", [])
        if not items:
            logger.info("지원사업 조회 결과 없음")
            return 0

        return self._save_items(items)

    def _save_items(self, items: list[dict]) -> int:
        """조회된 항목을 DB에 저장한다."""
        saved = 0
        session_gen = get_session()
        session = next(session_gen)
        try:
            for item in items:
                name = (
                    item.get("서비스명")
                    or item.get("사업명")
                    or item.get("name")
                    or ""
                ).strip()
                if not name:
                    continue

                # 중복 확인 (이름 + 주관기관)
                organizer = (
                    item.get("소관기관명")
                    or item.get("주관기관")
                    or item.get("organizer")
                    or ""
                ).strip()

                exists = session.execute(
                    select(SupportProgram.id).where(
                        SupportProgram.name == name,
                        SupportProgram.organizer == organizer,
                    )
                ).scalar_one_or_none()
                if exists:
                    continue

                program = SupportProgram(
                    name=name,
                    description=(
                        item.get("서비스목적요약")
                        or item.get("사업개요")
                        or item.get("description")
                        or ""
                    )[:1000],
                    organizer=organizer,
                    org_type=self._infer_org_type(organizer),
                    region=item.get("지역") or item.get("region") or "전국",
                    target_group=(
                        item.get("지원대상")
                        or item.get("대상")
                        or item.get("target_group")
                        or ""
                    ),
                    benefit=(
                        item.get("지원내용")
                        or item.get("급여내용")
                        or item.get("benefit")
                        or ""
                    ),
                    contact=(
                        item.get("문의처")
                        or item.get("연락처")
                        or item.get("contact")
                        or ""
                    ),
                    url=item.get("상세조회URL") or item.get("url") or "",
                    apply_start=self._parse_date(item.get("신청시작일")),
                    apply_end=self._parse_date(item.get("신청종료일")),
                    fetched_at=datetime.now(),
                )
                session.add(program)
                saved += 1

            session.commit()
            if saved:
                logger.info("지원사업 %d건 신규 저장", saved)
        except Exception:
            session.rollback()
            raise
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

        return saved

    @staticmethod
    def _infer_org_type(organizer: str) -> str:
        if any(w in organizer for w in ["부", "처", "청", "원", "법무", "여성가족", "고용노동"]):
            return "중앙"
        if any(w in organizer for w in ["도", "시", "군", "구"]):
            return "지자체"
        return "민간"

    @staticmethod
    def _parse_date(s: str | None) -> date | None:
        if not s:
            return None
        s = str(s).replace("-", "").replace("/", "").replace(".", "").strip()
        try:
            if len(s) == 8:
                return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        except (ValueError, IndexError):
            pass
        return None
