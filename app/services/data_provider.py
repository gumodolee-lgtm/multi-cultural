"""
데이터 제공자 — DB에서 데이터를 읽어 뷰에 전달하는 공통 인터페이스.
Mock 데이터 대신 실제 DB 쿼리를 사용한다.
DB에 데이터가 없으면 Mock 데이터로 폴백한다 (최초 실행 시).
"""
from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select, func, or_

from app.models.database import get_session, _SessionLocal
from app.models.news import News
from app.models.law import Law
from app.models.support import SupportProgram
from app.models.survey import SurveyStats

logger = logging.getLogger(__name__)


def _get_session():
    """세션을 직접 반환한다 (제너레이터 아닌 방식)."""
    if _SessionLocal is None:
        return None
    return _SessionLocal()


class DataProvider:
    """DB 기반 데이터 제공자"""

    # ------------------------------------------------------------------
    # 뉴스
    # ------------------------------------------------------------------
    @staticmethod
    def get_all_news() -> list[dict]:
        """전체 뉴스를 최신순으로 반환한다."""
        session = _get_session()
        if session is None:
            from app.ui.mock_data import MOCK_NEWS
            return list(MOCK_NEWS)
        try:
            rows = session.execute(
                select(News).order_by(News.published.desc())
            ).scalars().all()
            if not rows:
                from app.ui.mock_data import MOCK_NEWS
                return list(MOCK_NEWS)
            return [DataProvider._news_to_dict(r) for r in rows]
        finally:
            session.close()

    @staticmethod
    def search_news(keyword: str = "", category: str = "", source: str = "") -> list[dict]:
        """뉴스를 검색/필터링한다."""
        session = _get_session()
        if session is None:
            return []
        try:
            q = select(News).order_by(News.published.desc())
            if keyword:
                q = q.where(or_(
                    News.title.contains(keyword),
                    News.content.contains(keyword),
                ))
            if category and category != "전체":
                q = q.where(News.category == category)
            if source and source != "전체":
                q = q.where(News.source == source)
            rows = session.execute(q).scalars().all()
            return [DataProvider._news_to_dict(r) for r in rows]
        finally:
            session.close()

    @staticmethod
    def _news_to_dict(n: News) -> dict:
        return {
            "id": n.id,
            "title": n.title,
            "content": n.content or "",
            "summary": n.summary or "",
            "url": n.url,
            "source": n.source or "",
            "category": n.category or "",
            "published": n.published.strftime("%Y-%m-%d") if n.published else "",
            "is_bookmarked": n.is_bookmarked,
        }

    # ------------------------------------------------------------------
    # 법령
    # ------------------------------------------------------------------
    @staticmethod
    def get_all_laws() -> list[dict]:
        """전체 법령을 반환한다."""
        session = _get_session()
        if session is None:
            from app.ui.mock_data import MOCK_LAWS
            return list(MOCK_LAWS)
        try:
            rows = session.execute(
                select(Law).order_by(Law.amended_date.desc())
            ).scalars().all()
            if not rows:
                from app.ui.mock_data import MOCK_LAWS
                return list(MOCK_LAWS)
            return [DataProvider._law_to_dict(r) for r in rows]
        finally:
            session.close()

    @staticmethod
    def search_laws(keyword: str = "", category: str = "") -> list[dict]:
        """법령을 검색/필터링한다."""
        session = _get_session()
        if session is None:
            return []
        try:
            q = select(Law).order_by(Law.amended_date.desc())
            if keyword:
                q = q.where(or_(
                    Law.name.contains(keyword),
                    Law.content.contains(keyword),
                    Law.summary.contains(keyword),
                ))
            if category and category != "전체":
                q = q.where(Law.category == category)
            rows = session.execute(q).scalars().all()
            return [DataProvider._law_to_dict(r) for r in rows]
        finally:
            session.close()

    @staticmethod
    def _law_to_dict(l: Law) -> dict:
        return {
            "id": l.id,
            "law_code": l.law_code,
            "name": l.name,
            "category": l.category or "",
            "content": l.content or "",
            "summary": l.summary or "",
            "amended_date": str(l.amended_date) if l.amended_date else "",
            "effective_date": str(l.effective_date) if l.effective_date else "",
            "is_bookmarked": l.is_bookmarked,
        }

    # ------------------------------------------------------------------
    # 지원사업
    # ------------------------------------------------------------------
    @staticmethod
    def get_all_support() -> list[dict]:
        """전체 지원사업을 반환한다."""
        session = _get_session()
        if session is None:
            from app.ui.mock_data import MOCK_SUPPORT
            return list(MOCK_SUPPORT)
        try:
            rows = session.execute(
                select(SupportProgram).order_by(SupportProgram.apply_end.asc())
            ).scalars().all()
            if not rows:
                from app.ui.mock_data import MOCK_SUPPORT
                return list(MOCK_SUPPORT)
            return [DataProvider._support_to_dict(r) for r in rows]
        finally:
            session.close()

    @staticmethod
    def search_support(keyword: str = "", org_type: str = "", region: str = "") -> list[dict]:
        """지원사업을 검색/필터링한다."""
        session = _get_session()
        if session is None:
            return []
        try:
            q = select(SupportProgram).order_by(SupportProgram.apply_end.asc())
            if keyword:
                q = q.where(or_(
                    SupportProgram.name.contains(keyword),
                    SupportProgram.description.contains(keyword),
                    SupportProgram.benefit.contains(keyword),
                ))
            if org_type and org_type != "전체":
                q = q.where(SupportProgram.org_type == org_type)
            if region and region != "전체":
                q = q.where(SupportProgram.region == region)
            rows = session.execute(q).scalars().all()
            return [DataProvider._support_to_dict(r) for r in rows]
        finally:
            session.close()

    @staticmethod
    def _support_to_dict(s: SupportProgram) -> dict:
        return {
            "id": s.id,
            "name": s.name,
            "description": s.description or "",
            "organizer": s.organizer or "",
            "org_type": s.org_type or "",
            "region": s.region or "",
            "target_group": s.target_group or "",
            "benefit": s.benefit or "",
            "apply_start": str(s.apply_start) if s.apply_start else "",
            "apply_end": str(s.apply_end) if s.apply_end else "",
            "contact": s.contact or "",
            "url": s.url or "",
            "is_bookmarked": s.is_bookmarked,
        }

    # ------------------------------------------------------------------
    # 대시보드 KPI
    # ------------------------------------------------------------------
    @staticmethod
    def get_dashboard_stats() -> dict:
        """대시보드 통계를 반환한다."""
        session = _get_session()
        if session is None:
            from app.ui.mock_data import MOCK_DASHBOARD
            return dict(MOCK_DASHBOARD)
        try:
            today = datetime.now().date()
            news_count = session.execute(select(func.count(News.id))).scalar() or 0
            law_count = session.execute(select(func.count(Law.id))).scalar() or 0
            support_count = session.execute(select(func.count(SupportProgram.id))).scalar() or 0

            today_news = session.execute(
                select(func.count(News.id)).where(
                    func.date(News.published) == today
                )
            ).scalar() or 0

            closing_soon = session.execute(
                select(func.count(SupportProgram.id)).where(
                    SupportProgram.apply_end != None,
                    func.date(SupportProgram.apply_end) >= today,
                    func.julianday(SupportProgram.apply_end) - func.julianday(func.date('now')) <= 7,
                )
            ).scalar() or 0

            bookmarked = (
                (session.execute(select(func.count(News.id)).where(News.is_bookmarked == True)).scalar() or 0)
                + (session.execute(select(func.count(Law.id)).where(Law.is_bookmarked == True)).scalar() or 0)
                + (session.execute(select(func.count(SupportProgram.id)).where(SupportProgram.is_bookmarked == True)).scalar() or 0)
            )

            result = {
                "news_count": news_count,
                "law_count": law_count,
                "support_count": support_count,
                "today_news": today_news,
                "closing_soon": closing_soon,
                "bookmarked": bookmarked,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }

            # DB가 비어있으면 Mock 폴백
            if news_count == 0 and law_count == 0:
                from app.ui.mock_data import MOCK_DASHBOARD
                return dict(MOCK_DASHBOARD)

            return result
        finally:
            session.close()

    # ------------------------------------------------------------------
    # 북마크 토글
    # ------------------------------------------------------------------
    @staticmethod
    def toggle_bookmark(kind: str, item_id: int) -> bool:
        """북마크 상태를 토글한다. 토글 후 새 상태(True/False)를 반환."""
        model_map = {"news": News, "law": Law, "support": SupportProgram}
        model = model_map.get(kind)
        if model is None:
            return False

        session = _get_session()
        if session is None:
            return False
        try:
            row = session.get(model, item_id)
            if row is None:
                return False
            row.is_bookmarked = not row.is_bookmarked
            new_state = row.is_bookmarked
            session.commit()
            return new_state
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    # ------------------------------------------------------------------
    # 다문화가족실태조사 통계
    # ------------------------------------------------------------------
    @staticmethod
    def get_survey_stats() -> list[dict]:
        """다문화가족실태조사 통계 데이터를 반환한다."""
        session = _get_session()
        if session is None:
            return []
        try:
            rows = session.execute(
                select(SurveyStats).order_by(SurveyStats.survey_year.desc())
            ).scalars().all()
            return [
                {
                    "id": r.id,
                    "approval_no": r.approval_no,
                    "survey_name": r.survey_name,
                    "cycle": r.cycle or "",
                    "survey_year": r.survey_year,
                    "data_created": r.data_created or "",
                }
                for r in rows
            ]
        finally:
            session.close()

    # ------------------------------------------------------------------
    # 키워드 기반 필터 (생활영역 뷰용)
    # ------------------------------------------------------------------
    @staticmethod
    def filter_news_by_keywords(keywords: list[str]) -> list[dict]:
        """키워드로 뉴스를 필터링한다."""
        all_news = DataProvider.get_all_news()
        return [n for n in all_news
                if any(kw.lower() in (n["title"] + n["content"]).lower() for kw in keywords)]

    @staticmethod
    def filter_laws_by_keywords(keywords: list[str]) -> list[dict]:
        """키워드로 법령을 필터링한다."""
        all_laws = DataProvider.get_all_laws()
        return [l for l in all_laws
                if any(kw.lower() in (l["name"] + l.get("summary", "")).lower() for kw in keywords)]

    @staticmethod
    def filter_support_by_keywords(keywords: list[str]) -> list[dict]:
        """키워드로 지원사업을 필터링한다."""
        all_support = DataProvider.get_all_support()
        return [s for s in all_support
                if any(kw.lower() in (s["name"] + s["description"] + s.get("benefit", "")).lower() for kw in keywords)]
