"""
지원사업 수집 서비스 — 정부24 공공서비스 API에서 다문화 관련 지원사업을 수집한다.

정부24 공공서비스 정보 오픈 API (data.go.kr #15113968)
- 서비스 목록: /api/gov24/v1/serviceList
- 서비스 상세: /api/gov24/v1/serviceDetail
- 지원 조건: /api/gov24/v1/supportConditions
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

# 다문화 관련 키워드 — 서비스 목록에서 필터링용
_MULTICULTURAL_KEYWORDS = [
    "다문화", "외국인", "이민자", "결혼이민", "귀화",
    "체류", "비자", "국적", "이중언어", "다누리",
]


class SupportService:
    """정부24 공공서비스 API 기반 지원사업 수집기"""

    # 정부24 공공서비스 정보 API (2024년 엔드포인트 이전)
    SERVICE_LIST_URL = "https://api.odcloud.kr/api/gov24/v1/serviceList"
    SERVICE_DETAIL_URL = "https://api.odcloud.kr/api/gov24/v1/serviceDetail"

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
        """정부24 서비스 목록에서 다문화 관련 항목을 수집한다."""
        all_items: list[dict] = []

        for page in range(1, 6):  # 최대 5페이지 (250건)
            params = {
                "page": page,
                "perPage": 50,
                "serviceKey": self._api_key,
            }

            try:
                resp = requests.get(
                    self.SERVICE_LIST_URL, params=params, timeout=self._timeout,
                )
                data = resp.json()
            except requests.RequestException as e:
                logger.warning("정부24 서비스 목록 요청 실패 (page=%d): %s", page, e)
                break
            except ValueError:
                logger.warning("정부24 응답 JSON 파싱 실패 (status=%d)", resp.status_code)
                break

            # API 에러 코드 확인 (등록되지 않은 서비스 등)
            if isinstance(data, dict) and data.get("code") and data["code"] < 0:
                logger.warning(
                    "정부24 API 오류 (code=%d) — data.go.kr에서 "
                    "'행정안전부_대한민국 공공서비스(혜택) 정보' API 활용 신청이 필요합니다",
                    data["code"],
                )
                return 0

            items = data.get("data", [])
            if not items:
                break

            # 다문화 관련 키워드로 필터링
            for item in items:
                text = " ".join(str(v) for v in item.values() if v)
                if any(kw in text for kw in _MULTICULTURAL_KEYWORDS):
                    all_items.append(item)

            # 마지막 페이지 확인
            total_count = data.get("totalCount", 0)
            if page * 50 >= total_count:
                break

        if not all_items:
            logger.info("다문화 관련 지원사업 조회 결과 없음")
            return 0

        logger.info("다문화 관련 지원사업 %d건 발견", len(all_items))
        return self._save_items(all_items)

    def _save_items(self, items: list[dict]) -> int:
        """조회된 항목을 DB에 저장한다."""
        saved = 0
        session_gen = get_session()
        session = next(session_gen)
        try:
            for item in items:
                # gov24 API 필드명 우선, 기존 한글 필드명 폴백
                name = (
                    item.get("서비스명")
                    or item.get("SVC_NM")
                    or item.get("사업명")
                    or item.get("name")
                    or ""
                ).strip()
                if not name:
                    continue

                organizer = (
                    item.get("소관기관명")
                    or item.get("JURMNOF_NM")
                    or item.get("주관기관")
                    or item.get("organizer")
                    or ""
                ).strip()

                # 중복 확인 (이름 + 주관기관)
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
                        or item.get("SVC_PURPS_SMRY")
                        or item.get("사업개요")
                        or item.get("description")
                        or ""
                    )[:1000],
                    organizer=organizer,
                    org_type=self._infer_org_type(organizer),
                    region=item.get("지역") or item.get("region") or "전국",
                    target_group=(
                        item.get("지원대상")
                        or item.get("SPRT_TRGT_CN")
                        or item.get("대상")
                        or item.get("target_group")
                        or ""
                    ),
                    benefit=(
                        item.get("지원내용")
                        or item.get("ALWN_ITM_CN")
                        or item.get("급여내용")
                        or item.get("benefit")
                        or ""
                    ),
                    contact=(
                        item.get("문의처")
                        or item.get("INQR_CN")
                        or item.get("연락처")
                        or item.get("contact")
                        or ""
                    ),
                    url=(
                        item.get("상세조회URL")
                        or item.get("APPL_URL_ADDR")
                        or item.get("url")
                        or ""
                    ),
                    apply_start=self._parse_date(
                        item.get("신청시작일") or item.get("RCPT_BGNG_DT")
                    ),
                    apply_end=self._parse_date(
                        item.get("신청종료일") or item.get("RCPT_END_DT")
                    ),
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
