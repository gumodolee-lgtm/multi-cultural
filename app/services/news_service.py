"""
뉴스 수집 서비스 — RSS 피드에서 다문화 관련 뉴스를 수집한다.

수집 흐름:
1. 등록된 RSS 피드 목록에서 feedparser로 파싱
2. 키워드 필터링 (config.yaml의 news.keywords)
3. 중복 제거 (URL 기준)
4. DB 저장
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import feedparser
import requests
from sqlalchemy import select

from app.models.database import get_session
from app.models.news import News

if TYPE_CHECKING:
    from app.utils.config_loader import AppConfig

logger = logging.getLogger(__name__)

# 한국 주요 언론사 RSS (다문화/사회 관련 카테고리)
DEFAULT_RSS_FEEDS = [
    {"name": "연합뉴스 사회", "url": "https://www.yna.co.kr/rss/society.xml", "enabled": True},
    {"name": "KBS 사회", "url": "https://news.kbs.co.kr/news/pc/main/rss/rss_society.xml", "enabled": True},
    {"name": "한겨레 사회", "url": "https://www.hani.co.kr/rss/society/", "enabled": True},
]


class NewsService:
    """RSS 기반 뉴스 수집기"""

    def __init__(self, config: AppConfig):
        self._config = config
        self._keywords = config.news_keywords or [
            "다문화", "결혼이민", "외국인 주민", "이주민", "다문화가족", "귀화",
        ]
        self._max_days = config.news_max_days
        self._feeds = DEFAULT_RSS_FEEDS
        self._timeout = 15

    def fetch_all(self) -> int:
        """모든 RSS 피드에서 뉴스를 수집한다. 새로 저장된 건수를 반환."""
        total_saved = 0
        for feed_info in self._feeds:
            if not feed_info.get("enabled", True):
                continue
            try:
                count = self._fetch_feed(feed_info["name"], feed_info["url"])
                total_saved += count
                logger.info("RSS [%s] %d건 수집", feed_info["name"], count)
            except Exception:
                logger.exception("RSS [%s] 수집 실패", feed_info["name"])
        self._cleanup_old()
        return total_saved

    def _fetch_feed(self, source_name: str, url: str) -> int:
        """단일 RSS 피드를 파싱하여 DB에 저장한다."""
        try:
            resp = requests.get(url, timeout=self._timeout)
            resp.raise_for_status()
        except requests.RequestException:
            logger.warning("RSS 요청 실패: %s", url)
            return 0

        feed = feedparser.parse(resp.text)
        saved = 0

        session_gen = get_session()
        session = next(session_gen)
        try:
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                if not title or not link:
                    continue

                # 키워드 필터
                text = title + " " + entry.get("summary", "")
                if not any(kw in text for kw in self._keywords):
                    continue

                # 중복 확인
                exists = session.execute(
                    select(News.id).where(News.url == link)
                ).scalar_one_or_none()
                if exists:
                    continue

                # 발행일 파싱
                published = None
                if entry.get("published_parsed"):
                    try:
                        published = datetime(*entry.published_parsed[:6])
                    except (TypeError, ValueError):
                        pass

                # 카테고리 추론
                category = self._infer_category(text)

                news = News(
                    title=title,
                    content=entry.get("summary", "")[:500],
                    url=link,
                    source=source_name,
                    category=category,
                    published=published or datetime.now(),
                )
                session.add(news)
                saved += 1

            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

        return saved

    def _infer_category(self, text: str) -> str:
        """텍스트 내용으로 카테고리를 추론한다."""
        if any(w in text for w in ["정책", "법안", "시행", "개정", "입법"]):
            return "정책"
        if any(w in text for w in ["지역", "도", "시", "군", "구청"]):
            return "지역"
        if any(w in text for w in ["유엔", "UN", "국제", "해외"]):
            return "국제"
        return "사례"

    def _cleanup_old(self) -> None:
        """오래된 뉴스를 삭제한다."""
        cutoff = datetime.now() - timedelta(days=self._max_days)
        session_gen = get_session()
        session = next(session_gen)
        try:
            old = session.execute(
                select(News).where(News.fetched_at < cutoff, News.is_bookmarked == False)
            ).scalars().all()
            for item in old:
                session.delete(item)
            if old:
                session.commit()
                logger.info("오래된 뉴스 %d건 삭제", len(old))
        except Exception:
            session.rollback()
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass
