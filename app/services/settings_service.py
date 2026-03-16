"""설정 저장/로드 서비스 — AppSetting 테이블을 통한 key-value 영구 저장"""
from __future__ import annotations

import logging

from app.models.database import _SessionLocal
from app.models.settings import AppSetting

logger = logging.getLogger(__name__)

# 기본값 정의
_DEFAULTS = {
    "language": "ko",
    "theme": "light",          # light | dark
    "font_size": "13pt",
    "default_region": "전국",
    "notify_law": "true",
    "notify_news": "true",
    "notify_support_deadline": "true",
    "notify_keyword": "false",
    "news_interval_min": "60",
    "law_interval_hr": "24",
    "support_interval_hr": "12",
}


def _get_session():
    if _SessionLocal is None:
        return None
    return _SessionLocal()


def get_setting(key: str) -> str:
    """설정 값을 읽는다. DB에 없으면 기본값 반환."""
    session = _get_session()
    if session is None:
        return _DEFAULTS.get(key, "")
    try:
        row = session.get(AppSetting, key)
        if row and row.value is not None:
            return row.value
        return _DEFAULTS.get(key, "")
    finally:
        session.close()


def set_setting(key: str, value: str) -> None:
    """설정 값을 저장한다."""
    session = _get_session()
    if session is None:
        return
    try:
        row = session.get(AppSetting, key)
        if row:
            row.value = value
        else:
            session.add(AppSetting(key=key, value=value))
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("설정 저장 실패: %s=%s", key, value)
    finally:
        session.close()


def get_all_settings() -> dict[str, str]:
    """모든 설정을 딕셔너리로 반환한다."""
    result = dict(_DEFAULTS)
    session = _get_session()
    if session is None:
        return result
    try:
        rows = session.query(AppSetting).all()
        for row in rows:
            if row.value is not None:
                result[row.key] = row.value
        return result
    finally:
        session.close()
