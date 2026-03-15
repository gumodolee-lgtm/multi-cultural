"""
법령 수집 서비스 — 법제처 Open API에서 다문화 관련 법령을 조회/저장한다.

API 문서: https://www.law.go.kr/LSW/openApi.do
- 법령 검색: /DRF/lawSearch.do?OC=xxx&target=law&query=다문화&type=XML
- 법령 본문: /DRF/lawService.do?OC=xxx&MST=법령MST코드&type=XML
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

import requests
from sqlalchemy import select

from app.models.database import get_session
from app.models.law import Law

if TYPE_CHECKING:
    from app.utils.config_loader import AppConfig

logger = logging.getLogger(__name__)


class LawService:
    """법제처 Open API 연동"""

    BASE_URL = "https://www.law.go.kr/DRF/lawSearch.do"

    def __init__(self, config: AppConfig):
        self._config = config
        self._oc = config.law_api_key  # 법제처 OC 코드
        self._target_laws = config.law_target_laws or [
            "다문화가족지원법",
            "재한외국인 처우 기본법",
            "출입국관리법",
            "국적법",
            "외국인근로자의 고용 등에 관한 법률",
            "난민법",
        ]
        self._timeout = 20

    def fetch_all(self) -> int:
        """대상 법령을 모두 조회하여 DB에 저장/갱신한다. 처리 건수를 반환."""
        total = 0
        for law_name in self._target_laws:
            try:
                count = self._search_and_save(law_name)
                total += count
            except Exception:
                logger.exception("법령 수집 실패: %s", law_name)
        return total

    def _search_and_save(self, query: str) -> int:
        """법령명으로 검색하여 DB에 저장한다."""
        params = {
            "OC": self._oc,
            "target": "law",
            "type": "XML",
            "query": query,
            "display": "5",
        }

        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=self._timeout)
            resp.raise_for_status()
        except requests.RequestException:
            logger.warning("법제처 API 요청 실패: %s", query)
            return 0

        # XML 파싱
        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError:
            logger.warning("법제처 XML 파싱 실패: %s", query)
            return 0

        saved = 0
        session_gen = get_session()
        session = next(session_gen)
        try:
            for item in root.findall(".//law"):
                law_code = self._text(item, "법령일련번호") or self._text(item, "법령MST")
                name = self._text(item, "법령명한글") or self._text(item, "법령명")
                if not law_code or not name:
                    continue

                # 중복 확인 — law_code 기준 upsert
                existing = session.execute(
                    select(Law).where(Law.law_code == law_code)
                ).scalar_one_or_none()

                amended_str = self._text(item, "시행일자") or self._text(item, "공포일자")
                amended_date = self._parse_date(amended_str)

                category = self._infer_category(name)

                if existing:
                    # 기존 법령 갱신
                    existing.name = name
                    existing.category = category
                    if amended_date:
                        existing.amended_date = amended_date
                    existing.fetched_at = datetime.now()
                else:
                    law = Law(
                        law_code=law_code,
                        name=name,
                        category=category,
                        amended_date=amended_date,
                        fetched_at=datetime.now(),
                    )
                    session.add(law)
                    saved += 1

            session.commit()
            if saved:
                logger.info("법령 '%s' → %d건 신규 저장", query, saved)
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
    def _text(el: ET.Element, tag: str) -> str | None:
        child = el.find(tag)
        return child.text.strip() if child is not None and child.text else None

    @staticmethod
    def _parse_date(s: str | None) -> date | None:
        if not s:
            return None
        s = s.replace("-", "").replace("/", "").replace(".", "").strip()
        try:
            if len(s) == 8:
                return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        except (ValueError, IndexError):
            pass
        return None

    @staticmethod
    def _infer_category(name: str) -> str:
        if "다문화" in name or "난민" in name:
            return "다문화"
        if "출입국" in name or "비자" in name:
            return "출입국"
        if "국적" in name:
            return "국적"
        if "근로자" in name or "고용" in name:
            return "출입국"
        return "다문화"
