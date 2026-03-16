"""
config.yaml + .env 파일을 읽어 앱 전체에서 사용할 설정 객체를 제공한다.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv
import os

# PyInstaller로 패키징된 경우:
#   _ROOT = exe 위치 (사용자 파일: .env, data/)
#   _BUNDLE = _internal 디렉토리 (번들 파일: config.yaml)
# 개발 모드: 둘 다 소스 루트
if getattr(sys, 'frozen', False):
    _ROOT = Path(sys.executable).parent
    _BUNDLE = Path(getattr(sys, '_MEIPASS', _ROOT))
else:
    _ROOT = Path(__file__).parent.parent.parent
    _BUNDLE = _ROOT


@dataclass
class SchedulerConfig:
    news_interval_minutes: int = 60
    law_interval_hours: int = 24
    support_interval_hours: int = 12
    retry_count: int = 3
    retry_delay_seconds: int = 30


@dataclass
class AppConfig:
    name: str = "다문화 정보 허브"
    version: str = "0.1.0"
    language: str = "ko"
    window_width: int = 1280
    window_height: int = 800
    font_size: int = 13
    db_path: str = "data/michub.db"
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    law_target_laws: list[str] = field(default_factory=list)
    news_keywords: list[str] = field(default_factory=list)
    news_max_days: int = 90
    # API 키 (환경 변수에서)
    public_data_api_key: str = ""
    multicultural_survey_api_key: str = ""
    law_api_key: str = ""
    deepl_api_key: str = ""
    anthropic_api_key: str = ""


_config: AppConfig | None = None


def load_config(config_path: Path | None = None) -> AppConfig:
    """config.yaml과 .env를 읽어 AppConfig를 반환한다. 이미 로드된 경우 캐시를 반환."""
    global _config
    if _config is not None:
        return _config

    # .env 파일 로드 — exe 옆 → _internal 순으로 탐색
    for candidate in [_ROOT / ".env", _BUNDLE / ".env"]:
        if candidate.exists():
            load_dotenv(candidate)
            break

    # config.yaml 로드 — _internal(번들) → exe 옆 순으로 탐색
    yaml_path = config_path
    if yaml_path is None:
        for candidate in [_BUNDLE / "config.yaml", _ROOT / "config.yaml"]:
            if candidate.exists():
                yaml_path = candidate
                break
        else:
            yaml_path = _ROOT / "config.yaml"  # 기본값 (없어도 빈 dict로 처리)
    raw: dict = {}
    if yaml_path.exists():
        with open(yaml_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

    app_raw = raw.get("app", {})
    db_raw = raw.get("database", {})
    sched_raw = raw.get("scheduler", {})
    law_raw = raw.get("law_api", {})
    news_raw = raw.get("news", {})

    _config = AppConfig(
        name=app_raw.get("name", "다문화 정보 허브"),
        version=app_raw.get("version", "0.1.0"),
        language=app_raw.get("language", "ko"),
        window_width=app_raw.get("window_width", 1280),
        window_height=app_raw.get("window_height", 800),
        font_size=app_raw.get("font_size", 13),
        db_path=db_raw.get("path", "data/michub.db"),
        scheduler=SchedulerConfig(
            news_interval_minutes=sched_raw.get("news_interval_minutes", 60),
            law_interval_hours=sched_raw.get("law_interval_hours", 24),
            support_interval_hours=sched_raw.get("support_interval_hours", 12),
            retry_count=sched_raw.get("retry_count", 3),
            retry_delay_seconds=sched_raw.get("retry_delay_seconds", 30),
        ),
        law_target_laws=law_raw.get("target_laws", []),
        news_keywords=news_raw.get("keywords", []),
        news_max_days=news_raw.get("max_days", 90),
        # 환경 변수에서 API 정보 로드
        public_data_api_key=os.getenv("PUBLIC_DATA_API_KEY", ""),
        multicultural_survey_api_key=os.getenv("MULTICULTURAL_SURVEY_API_KEY", ""),
        law_api_key=os.getenv("LAW_API_OC", ""),   # 법제처 OC 파라미터 (.env에 설정 필요)
        deepl_api_key=os.getenv("DEEPL_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
    )
    return _config
