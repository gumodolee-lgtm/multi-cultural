"""
DB 시딩 — 첫 실행 시 Mock 데이터를 DB에 삽입한다.
DB에 이미 데이터가 있으면 건너뛴다.
"""
from __future__ import annotations

import logging
from datetime import datetime, date

from sqlalchemy import select, func

from app.models.database import _SessionLocal
from app.models.news import News
from app.models.law import Law
from app.models.support import SupportProgram

logger = logging.getLogger(__name__)


def seed_if_empty() -> None:
    """DB가 비어있으면 초기 데이터를 삽입한다."""
    if _SessionLocal is None:
        logger.warning("DB 세션 없음 — 시딩 건너뜀")
        return

    session = _SessionLocal()
    try:
        news_count = session.execute(select(func.count(News.id))).scalar() or 0
        law_count = session.execute(select(func.count(Law.id))).scalar() or 0
        support_count = session.execute(select(func.count(SupportProgram.id))).scalar() or 0

        if news_count > 0 or law_count > 0 or support_count > 0:
            logger.info("DB에 기존 데이터 있음 (뉴스 %d, 법령 %d, 지원 %d) — 시딩 건너뜀",
                        news_count, law_count, support_count)
            return

        logger.info("DB 비어있음 — 초기 데이터 시딩 시작")
        _seed_news(session)
        _seed_laws(session)
        _seed_support(session)
        session.commit()
        logger.info("초기 데이터 시딩 완료")
    except Exception:
        session.rollback()
        logger.exception("시딩 실패")
    finally:
        session.close()


def _seed_news(session) -> None:
    """뉴스 초기 데이터"""
    from app.ui.mock_data import MOCK_NEWS
    for item in MOCK_NEWS:
        published = None
        if item.get("published"):
            try:
                published = datetime.strptime(item["published"], "%Y-%m-%d")
            except (ValueError, TypeError):
                published = datetime.now()

        news = News(
            title=item["title"],
            content=item.get("content", ""),
            summary=item.get("summary", ""),
            url=item["url"],
            source=item.get("source", ""),
            category=item.get("category", ""),
            published=published or datetime.now(),
            is_bookmarked=item.get("is_bookmarked", False),
        )
        session.add(news)
    logger.info("뉴스 %d건 시딩", len(MOCK_NEWS))


def _seed_laws(session) -> None:
    """법령 초기 데이터"""
    from app.ui.mock_data import MOCK_LAWS
    for item in MOCK_LAWS:
        amended = _parse_date(item.get("amended_date"))
        effective = _parse_date(item.get("effective_date"))

        law = Law(
            law_code=item["law_code"],
            name=item["name"],
            category=item.get("category", ""),
            content=item.get("content", ""),
            summary=item.get("summary", ""),
            amended_date=amended,
            effective_date=effective,
            is_bookmarked=item.get("is_bookmarked", False),
        )
        session.add(law)
    logger.info("법령 %d건 시딩", len(MOCK_LAWS))


def _seed_support(session) -> None:
    """지원사업 초기 데이터"""
    from app.ui.mock_data import MOCK_SUPPORT
    for item in MOCK_SUPPORT:
        program = SupportProgram(
            name=item["name"],
            description=item.get("description", ""),
            organizer=item.get("organizer", ""),
            org_type=item.get("org_type", ""),
            region=item.get("region", ""),
            target_group=item.get("target_group", ""),
            benefit=item.get("benefit", ""),
            apply_start=_parse_date(item.get("apply_start")),
            apply_end=_parse_date(item.get("apply_end")),
            contact=item.get("contact", ""),
            url=item.get("url", ""),
            is_bookmarked=item.get("is_bookmarked", False),
        )
        session.add(program)
    logger.info("지원사업 %d건 시딩", len(MOCK_SUPPORT))


def _parse_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
