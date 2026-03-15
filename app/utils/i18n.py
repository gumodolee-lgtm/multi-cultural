"""
다국어 지원 (i18n) — 4개 언어 번역 시스템

지원 언어: ko(한국어), en(English), vi(Tiếng Việt), zh(中文)
사용법:
    from app.utils.i18n import tr, set_language
    set_language("en")
    tr("dashboard")  # → "Dashboard"
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# 현재 언어
_current_lang: str = "ko"

# 번역 사전: key → {lang: text}
_TRANSLATIONS: dict[str, dict[str, str]] = {
    # -- 메뉴 --
    "app_name": {
        "ko": "다문화 정보 허브",
        "en": "Multicultural Info Hub",
        "vi": "Trung tâm Thông tin Đa văn hóa",
        "zh": "多文化信息中心",
    },
    "home": {
        "ko": "홈",
        "en": "Home",
        "vi": "Trang chủ",
        "zh": "首页",
    },
    "dashboard": {
        "ko": "대시보드",
        "en": "Dashboard",
        "vi": "Bảng điều khiển",
        "zh": "仪表盘",
    },
    "visa": {
        "ko": "비자·체류",
        "en": "Visa & Stay",
        "vi": "Visa & Cư trú",
        "zh": "签证·居留",
    },
    "health": {
        "ko": "의료·복지",
        "en": "Health & Welfare",
        "vi": "Y tế & Phúc lợi",
        "zh": "医疗·福利",
    },
    "family": {
        "ko": "가족·육아",
        "en": "Family & Childcare",
        "vi": "Gia đình & Chăm sóc trẻ",
        "zh": "家庭·育儿",
    },
    "education": {
        "ko": "교육·문화",
        "en": "Education & Culture",
        "vi": "Giáo dục & Văn hóa",
        "zh": "教育·文化",
    },
    "job": {
        "ko": "일자리",
        "en": "Jobs",
        "vi": "Việc làm",
        "zh": "就业",
    },
    "news": {
        "ko": "뉴스·공지",
        "en": "News",
        "vi": "Tin tức",
        "zh": "新闻·公告",
    },
    "law": {
        "ko": "법령·규정",
        "en": "Laws & Regulations",
        "vi": "Pháp luật",
        "zh": "法令·规定",
    },
    "support": {
        "ko": "지원사업",
        "en": "Support Programs",
        "vi": "Chương trình hỗ trợ",
        "zh": "支援事业",
    },
    "search": {
        "ko": "통합 검색",
        "en": "Search",
        "vi": "Tìm kiếm",
        "zh": "综合搜索",
    },
    "bookmark": {
        "ko": "즐겨찾기",
        "en": "Bookmarks",
        "vi": "Đánh dấu",
        "zh": "收藏",
    },
    "settings": {
        "ko": "설정",
        "en": "Settings",
        "vi": "Cài đặt",
        "zh": "设置",
    },
    "help": {
        "ko": "도움말",
        "en": "Help",
        "vi": "Trợ giúp",
        "zh": "帮助",
    },

    # -- 공통 UI --
    "ready": {
        "ko": "준비",
        "en": "Ready",
        "vi": "Sẵn sàng",
        "zh": "就绪",
    },
    "auto_collection_active": {
        "ko": "자동 수집 활성화됨",
        "en": "Auto-collection active",
        "vi": "Thu thập tự động đang hoạt động",
        "zh": "自动采集已激活",
    },
    "refresh": {
        "ko": "새로고침",
        "en": "Refresh",
        "vi": "Làm mới",
        "zh": "刷新",
    },
    "export": {
        "ko": "데이터 내보내기",
        "en": "Export Data",
        "vi": "Xuất dữ liệu",
        "zh": "导出数据",
    },
    "no_results": {
        "ko": "검색 결과가 없습니다.",
        "en": "No results found.",
        "vi": "Không tìm thấy kết quả.",
        "zh": "没有搜索结果。",
    },
    "last_update": {
        "ko": "마지막 업데이트",
        "en": "Last updated",
        "vi": "Cập nhật lần cuối",
        "zh": "最后更新",
    },
    "collected_news": {
        "ko": "수집 뉴스",
        "en": "Collected News",
        "vi": "Tin đã thu thập",
        "zh": "收集的新闻",
    },
    "major_laws": {
        "ko": "주요 법령",
        "en": "Major Laws",
        "vi": "Luật chính",
        "zh": "主要法令",
    },
    "support_programs": {
        "ko": "지원사업",
        "en": "Programs",
        "vi": "Chương trình",
        "zh": "支援事业",
    },
    "today_news": {
        "ko": "오늘 뉴스",
        "en": "Today's News",
        "vi": "Tin hôm nay",
        "zh": "今日新闻",
    },
    "closing_soon": {
        "ko": "마감 임박",
        "en": "Closing Soon",
        "vi": "Sắp hết hạn",
        "zh": "即将截止",
    },
    "bookmarked": {
        "ko": "북마크",
        "en": "Bookmarked",
        "vi": "Đã đánh dấu",
        "zh": "已收藏",
    },
    "search_placeholder": {
        "ko": "키워드를 입력하세요...",
        "en": "Enter a keyword...",
        "vi": "Nhập từ khóa...",
        "zh": "请输入关键词...",
    },
    "deadline": {
        "ko": "마감",
        "en": "Closed",
        "vi": "Đã hết hạn",
        "zh": "已截止",
    },

    # -- 섹션 그룹 --
    "life_areas": {
        "ko": "생활 영역",
        "en": "Life Areas",
        "vi": "Lĩnh vực đời sống",
        "zh": "生活领域",
    },
    "information": {
        "ko": "정보",
        "en": "Information",
        "vi": "Thông tin",
        "zh": "信息",
    },
    "tools": {
        "ko": "도구",
        "en": "Tools",
        "vi": "Công cụ",
        "zh": "工具",
    },
}


def set_language(lang: str) -> None:
    """UI 언어를 변경한다."""
    global _current_lang
    if lang in ("ko", "en", "vi", "zh"):
        _current_lang = lang
        logger.info("언어 변경: %s", lang)
    else:
        logger.warning("지원하지 않는 언어: %s", lang)


def get_language() -> str:
    """현재 언어 코드를 반환한다."""
    return _current_lang


def tr(key: str) -> str:
    """번역 키를 현재 언어로 번역한다.

    번역이 없으면 한국어 텍스트, 그마저도 없으면 키 자체를 반환.
    """
    entry = _TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(_current_lang, entry.get("ko", key))


def get_supported_languages() -> list[tuple[str, str]]:
    """지원 언어 목록을 반환한다. [(code, display_name), ...]"""
    return [
        ("ko", "한국어"),
        ("en", "English"),
        ("vi", "Tiếng Việt"),
        ("zh", "中文"),
    ]
