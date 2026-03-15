"""
수집 작업 함수 — 스케줄러에서 호출하는 실제 수집 로직
각 함수는 독립적으로 실행 가능하며, 실패 시 다른 수집에 영향을 주지 않는다.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.utils.config_loader import AppConfig

logger = logging.getLogger(__name__)


def collect_news(config: AppConfig) -> int:
    """뉴스 RSS 수집 작업"""
    from app.services.news_service import NewsService
    service = NewsService(config)
    count = service.fetch_all()
    logger.info("뉴스 수집 완료: %d건", count)
    return count


def collect_laws(config: AppConfig) -> int:
    """법령 수집 작업"""
    from app.services.law_service import LawService
    service = LawService(config)
    count = service.fetch_all()
    logger.info("법령 수집 완료: %d건", count)
    return count


def collect_support(config: AppConfig) -> int:
    """지원사업 수집 작업"""
    from app.services.support_service import SupportService
    service = SupportService(config)
    count = service.fetch_all()

    # PDF 기반 지원센터 현황 파싱 (파일이 있을 때만)
    try:
        from app.services.pdf_parser import PdfParser
        parser = PdfParser(data_dir="data")
        pdf_count = parser.parse_and_save()
        count += pdf_count
    except Exception:
        logger.exception("PDF 파싱 실패")

    logger.info("지원사업 수집 완료: %d건", count)
    return count
