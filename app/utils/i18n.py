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

    # -- 대시보드 --
    "dashboard_title": {
        "ko": "📋 대시보드",
        "en": "📋 Dashboard",
        "vi": "📋 Bảng điều khiển",
        "zh": "📋 仪表盘",
    },
    "recent_news": {
        "ko": "📰 최근 뉴스",
        "en": "📰 Recent News",
        "vi": "📰 Tin mới nhất",
        "zh": "📰 最新新闻",
    },
    "closing_support": {
        "ko": "⏰ 마감 임박 지원사업",
        "en": "⏰ Closing Soon Programs",
        "vi": "⏰ Chương trình sắp hết hạn",
        "zh": "⏰ 即将截止的支援事业",
    },

    # -- 검색 --
    "search_title": {
        "ko": "🔍 통합 검색",
        "en": "🔍 Unified Search",
        "vi": "🔍 Tìm kiếm tổng hợp",
        "zh": "🔍 综合搜索",
    },
    "search_desc": {
        "ko": "뉴스, 법령, 지원사업을 한 번에 검색합니다",
        "en": "Search news, laws, and support programs at once",
        "vi": "Tìm kiếm tin tức, pháp luật và chương trình hỗ trợ cùng lúc",
        "zh": "一次搜索新闻、法令和支援事业",
    },
    "popular_keywords": {
        "ko": "💡 인기 검색어",
        "en": "💡 Popular Keywords",
        "vi": "💡 Từ khóa phổ biến",
        "zh": "💡 热门搜索词",
    },
    "search_result": {
        "ko": "검색 결과",
        "en": "Search Results",
        "vi": "Kết quả tìm kiếm",
        "zh": "搜索结果",
    },

    # -- 북마크 --
    "bookmark_title": {
        "ko": "⭐ 북마크",
        "en": "⭐ Bookmarks",
        "vi": "⭐ Đánh dấu",
        "zh": "⭐ 收藏",
    },
    "saved_items_count": {
        "ko": "총 {count}개 항목이 저장되어 있습니다",
        "en": "{count} items saved",
        "vi": "Đã lưu {count} mục",
        "zh": "共保存{count}个项目",
    },
    "no_saved_items": {
        "ko": "저장된 항목이 없습니다.",
        "en": "No saved items.",
        "vi": "Không có mục đã lưu.",
        "zh": "没有保存的项目。",
    },

    # -- 상세 --
    "view_source": {
        "ko": "🔗 원문 보기",
        "en": "🔗 View Source",
        "vi": "🔗 Xem nguồn",
        "zh": "🔗 查看原文",
    },
    "close": {
        "ko": "닫기",
        "en": "Close",
        "vi": "Đóng",
        "zh": "关闭",
    },
    "select_item": {
        "ko": "← 항목을 선택하세요",
        "en": "← Select an item",
        "vi": "← Chọn một mục",
        "zh": "← 请选择一个项目",
    },
    "no_content": {
        "ko": "(내용 없음)",
        "en": "(No content)",
        "vi": "(Không có nội dung)",
        "zh": "(无内容)",
    },

    # -- 필터/카테고리 --
    "all": {
        "ko": "전체",
        "en": "All",
        "vi": "Tất cả",
        "zh": "全部",
    },
    "news_search": {
        "ko": "뉴스 검색...",
        "en": "Search news...",
        "vi": "Tìm kiếm tin tức...",
        "zh": "搜索新闻...",
    },

    # -- 생활영역 --
    "related_news": {
        "ko": "📰 관련 뉴스",
        "en": "📰 Related News",
        "vi": "📰 Tin liên quan",
        "zh": "📰 相关新闻",
    },
    "related_laws": {
        "ko": "⚖️ 관련 법령",
        "en": "⚖️ Related Laws",
        "vi": "⚖️ Luật liên quan",
        "zh": "⚖️ 相关法令",
    },
    "related_support": {
        "ko": "🏛️ 관련 지원사업",
        "en": "🏛️ Related Programs",
        "vi": "🏛️ Chương trình liên quan",
        "zh": "🏛️ 相关支援事业",
    },
    "no_data_yet": {
        "ko": "아직 수집된 데이터가 없습니다.\n자동 수집이 시작되면 관련 정보가 여기에 표시됩니다.",
        "en": "No data collected yet.\nRelated information will appear here once auto-collection starts.",
        "vi": "Chưa có dữ liệu.\nThông tin liên quan sẽ hiển thị khi bắt đầu thu thập tự động.",
        "zh": "暂无数据。\n自动采集开始后，相关信息将显示在此处。",
    },

    # -- 설정 --
    "auto_collection": {
        "ko": "자동 수집",
        "en": "Auto Collection",
        "vi": "Thu thập tự động",
        "zh": "自动采集",
    },
    "manual_refresh": {
        "ko": "수동 새로고침",
        "en": "Manual Refresh",
        "vi": "Làm mới thủ công",
        "zh": "手动刷新",
    },

    # -- 법령 AI 요약 --
    "ai_summary": {
        "ko": "💡 AI 요약",
        "en": "💡 AI Summary",
        "vi": "💡 Tóm tắt AI",
        "zh": "💡 AI摘要",
    },
    "target": {
        "ko": "대상",
        "en": "Target Group",
        "vi": "Đối tượng",
        "zh": "对象",
    },
    "benefit": {
        "ko": "지원내용",
        "en": "Benefits",
        "vi": "Hỗ trợ",
        "zh": "支援内容",
    },
    "contact": {
        "ko": "연락처",
        "en": "Contact",
        "vi": "Liên hệ",
        "zh": "联系方式",
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
