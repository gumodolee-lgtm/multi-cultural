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

    # -- 메타데이터 --
    "source": {
        "ko": "출처",
        "en": "Source",
        "vi": "Nguồn",
        "zh": "来源",
    },
    "category": {
        "ko": "카테고리",
        "en": "Category",
        "vi": "Chuyên mục",
        "zh": "类别",
    },
    "published_date": {
        "ko": "게시일",
        "en": "Published",
        "vi": "Ngày đăng",
        "zh": "发布日期",
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

    # -- 설정 뷰 --
    "settings_title": {
        "ko": "⚙️ 설정",
        "en": "⚙️ Settings",
        "vi": "⚙️ Cài đặt",
        "zh": "⚙️ 设置",
    },
    "general": {
        "ko": "🌐 일반",
        "en": "🌐 General",
        "vi": "🌐 Chung",
        "zh": "🌐 一般",
    },
    "interface_lang": {
        "ko": "인터페이스 언어:",
        "en": "Interface language:",
        "vi": "Ngôn ngữ giao diện:",
        "zh": "界面语言：",
    },
    "theme": {
        "ko": "테마:",
        "en": "Theme:",
        "vi": "Chủ đề:",
        "zh": "主题：",
    },
    "theme_light": {
        "ko": "라이트",
        "en": "Light",
        "vi": "Sáng",
        "zh": "浅色",
    },
    "theme_dark": {
        "ko": "다크",
        "en": "Dark",
        "vi": "Tối",
        "zh": "深色",
    },
    "theme_system": {
        "ko": "시스템 설정 따르기",
        "en": "Follow system",
        "vi": "Theo hệ thống",
        "zh": "跟随系统",
    },
    "font_size": {
        "ko": "글자 크기:",
        "en": "Font size:",
        "vi": "Cỡ chữ:",
        "zh": "字体大小：",
    },
    "default_region": {
        "ko": "기본 지역:",
        "en": "Default region:",
        "vi": "Khu vực mặc định:",
        "zh": "默认地区：",
    },
    "notifications": {
        "ko": "🔔 알림",
        "en": "🔔 Notifications",
        "vi": "🔔 Thông báo",
        "zh": "🔔 通知",
    },
    "notify_law": {
        "ko": "법령 개정 알림",
        "en": "Law amendment notification",
        "vi": "Thông báo sửa đổi luật",
        "zh": "法令修订通知",
    },
    "notify_news": {
        "ko": "새 뉴스 알림",
        "en": "New news notification",
        "vi": "Thông báo tin mới",
        "zh": "新闻通知",
    },
    "notify_support_deadline": {
        "ko": "지원사업 마감 임박 알림 (D-7, D-1)",
        "en": "Support program deadline alert (D-7, D-1)",
        "vi": "Cảnh báo hạn chót chương trình (D-7, D-1)",
        "zh": "支援事业截止提醒 (D-7, D-1)",
    },
    "notify_keyword": {
        "ko": "관심 키워드 매칭 알림",
        "en": "Keyword matching notification",
        "vi": "Thông báo khớp từ khóa",
        "zh": "关键词匹配通知",
    },
    "manage_keywords": {
        "ko": "키워드 관리",
        "en": "Manage Keywords",
        "vi": "Quản lý từ khóa",
        "zh": "管理关键词",
    },
    "auto_update": {
        "ko": "🔄 자동 업데이트",
        "en": "🔄 Auto Update",
        "vi": "🔄 Cập nhật tự động",
        "zh": "🔄 自动更新",
    },
    "news_interval": {
        "ko": "뉴스 수집 주기:",
        "en": "News collection interval:",
        "vi": "Chu kỳ thu thập tin:",
        "zh": "新闻收集周期：",
    },
    "law_interval": {
        "ko": "법령 확인 주기:",
        "en": "Law check interval:",
        "vi": "Chu kỳ kiểm tra luật:",
        "zh": "法令检查周期：",
    },
    "support_interval": {
        "ko": "지원사업 확인 주기:",
        "en": "Program check interval:",
        "vi": "Chu kỳ kiểm tra chương trình:",
        "zh": "支援事业检查周期：",
    },
    "minutes": {
        "ko": " 분",
        "en": " min",
        "vi": " phút",
        "zh": " 分钟",
    },
    "hours": {
        "ko": " 시간",
        "en": " hrs",
        "vi": " giờ",
        "zh": " 小时",
    },
    "data_management": {
        "ko": "💾 데이터 관리",
        "en": "💾 Data Management",
        "vi": "💾 Quản lý dữ liệu",
        "zh": "💾 数据管理",
    },
    "update_now": {
        "ko": "🔄 지금 업데이트",
        "en": "🔄 Update Now",
        "vi": "🔄 Cập nhật ngay",
        "zh": "🔄 立即更新",
    },
    "export_data": {
        "ko": "📥 데이터 내보내기",
        "en": "📥 Export Data",
        "vi": "📥 Xuất dữ liệu",
        "zh": "📥 导出数据",
    },
    "reset_all": {
        "ko": "🗑️ 전체 초기화",
        "en": "🗑️ Reset All",
        "vi": "🗑️ Đặt lại tất cả",
        "zh": "🗑️ 全部重置",
    },
    "reset_confirm_title": {
        "ko": "데이터 초기화",
        "en": "Reset Data",
        "vi": "Đặt lại dữ liệu",
        "zh": "重置数据",
    },
    "reset_confirm_msg": {
        "ko": "정말로 모든 수집 데이터를 삭제하시겠습니까?\n(북마크 포함 전체 삭제)",
        "en": "Delete all collected data?\n(Including bookmarks)",
        "vi": "Xóa tất cả dữ liệu đã thu thập?\n(Bao gồm đánh dấu)",
        "zh": "确定删除所有数据吗？\n（包括收藏）",
    },
    "data_reset_done": {
        "ko": "데이터가 초기화되었습니다.",
        "en": "Data has been reset.",
        "vi": "Đã đặt lại dữ liệu.",
        "zh": "数据已重置。",
    },
    "about": {
        "ko": "ℹ️ 정보",
        "en": "ℹ️ About",
        "vi": "ℹ️ Thông tin",
        "zh": "ℹ️ 关于",
    },
    "updating": {
        "ko": "수동 업데이트 요청 중...",
        "en": "Requesting manual update...",
        "vi": "Đang yêu cầu cập nhật thủ công...",
        "zh": "正在请求手动更新...",
    },

    # -- 통계 --
    "survey_stats_title": {
        "ko": "📊 다문화가족 실태조사",
        "en": "📊 Multicultural Family Survey",
        "vi": "📊 Khảo sát Gia đình Đa văn hóa",
        "zh": "📊 多文化家庭实态调查",
    },
    "survey_year": {
        "ko": "조사 연도",
        "en": "Survey Year",
        "vi": "Năm khảo sát",
        "zh": "调查年份",
    },

    # -- 도움말 뷰 --
    "help_title": {
        "ko": "❓ 도움말",
        "en": "❓ Help",
        "vi": "❓ Trợ giúp",
        "zh": "❓ 帮助",
    },
    "help_subtitle": {
        "ko": "앱 사용법과 자주 묻는 질문을 확인하세요.",
        "en": "Learn how to use the app and check the FAQ.",
        "vi": "Tìm hiểu cách sử dụng và xem câu hỏi thường gặp.",
        "zh": "了解应用使用方法和常见问题。",
    },
    "faq_section": {
        "ko": "💡 자주 묻는 질문",
        "en": "💡 FAQ",
        "vi": "💡 Câu hỏi thường gặp",
        "zh": "💡 常见问题",
    },
    "faq_q1": {
        "ko": "이 프로그램은 무엇인가요?",
        "en": "What is this application?",
        "vi": "Ứng dụng này là gì?",
        "zh": "这个程序是什么？",
    },
    "faq_a1": {
        "ko": "다문화 정보 허브는 다문화가족과 이주민을 위한 뉴스, 법령, 지원사업 정보를 자동으로 수집하여 한곳에서 볼 수 있게 해주는 데스크탑 앱입니다.",
        "en": "Multicultural Info Hub is a desktop app that automatically collects news, laws, and support program information for multicultural families and immigrants.",
        "vi": "Trung tâm Thông tin Đa văn hóa là ứng dụng máy tính tự động thu thập tin tức, luật pháp và chương trình hỗ trợ cho gia đình đa văn hóa và người nhập cư.",
        "zh": "多文化信息中心是一款桌面应用，自动收集面向多文化家庭和移民的新闻、法令和支援事业信息。",
    },
    "faq_q2": {
        "ko": "정보는 어디서 가져오나요?",
        "en": "Where does the information come from?",
        "vi": "Thông tin được lấy từ đâu?",
        "zh": "信息来自哪里？",
    },
    "faq_a2": {
        "ko": "뉴스는 주요 언론사 RSS 피드에서, 법령은 법제처 Open API에서, 지원사업은 공공데이터포털 API에서 자동으로 수집합니다.",
        "en": "News from major media RSS feeds, laws from the Legislation API, and support programs from the Public Data Portal API.",
        "vi": "Tin tức từ RSS các hãng tin lớn, luật từ API Cơ quan Lập pháp, chương trình hỗ trợ từ API Cổng Dữ liệu Công khai.",
        "zh": "新闻来自主要媒体RSS，法令来自法制处API，支援事业来自公共数据门户API。",
    },
    "faq_q3": {
        "ko": "데이터는 얼마나 자주 업데이트되나요?",
        "en": "How often is data updated?",
        "vi": "Dữ liệu được cập nhật thường xuyên không?",
        "zh": "数据多久更新一次？",
    },
    "faq_a3": {
        "ko": "뉴스는 매 1시간, 법령은 24시간, 지원사업은 12시간마다 자동으로 갱신됩니다. 설정 메뉴에서 주기를 변경할 수 있습니다.",
        "en": "News every 1 hour, laws every 24 hours, programs every 12 hours. You can change the interval in Settings.",
        "vi": "Tin tức mỗi 1 giờ, luật mỗi 24 giờ, chương trình mỗi 12 giờ. Bạn có thể thay đổi trong Cài đặt.",
        "zh": "新闻每1小时，法令每24小时，支援事业每12小时自动更新。可在设置中更改。",
    },
    "faq_q4": {
        "ko": "'생활 영역' 메뉴는 무엇인가요?",
        "en": "What is the 'Life Areas' menu?",
        "vi": "Menu 'Lĩnh vực đời sống' là gì?",
        "zh": "'生活领域'菜单是什么？",
    },
    "faq_a4": {
        "ko": "비자·체류, 의료·복지, 가족·육아, 교육·문화, 일자리 등 생활 분야별로 관련 뉴스+법령+지원사업을 한눈에 볼 수 있는 통합 화면입니다.",
        "en": "An integrated view showing related news, laws, and programs by life area: Visa, Health, Family, Education, and Jobs.",
        "vi": "Màn hình tổng hợp hiển thị tin tức, luật pháp và chương trình liên quan theo lĩnh vực: Visa, Y tế, Gia đình, Giáo dục và Việc làm.",
        "zh": "按签证、医疗、家庭、教育、就业等生活领域，综合展示相关新闻+法令+支援事业的画面。",
    },
    "faq_q5": {
        "ko": "즐겨찾기는 어떻게 사용하나요?",
        "en": "How do I use bookmarks?",
        "vi": "Làm thế nào để sử dụng đánh dấu?",
        "zh": "如何使用收藏功能？",
    },
    "faq_a5": {
        "ko": "각 뉴스, 법령, 지원사업 카드의 ☆ 버튼을 누르면 즐겨찾기에 추가됩니다. 즐겨찾기 메뉴에서 저장한 항목을 모아볼 수 있습니다.",
        "en": "Click the ☆ button on any news, law, or program card to bookmark it. View saved items in the Bookmarks menu.",
        "vi": "Nhấn nút ☆ trên thẻ tin tức, luật hoặc chương trình để đánh dấu. Xem mục đã lưu trong menu Đánh dấu.",
        "zh": "点击新闻、法令或支援事业卡片上的☆按钮即可收藏。在收藏菜单中查看已保存项目。",
    },
    "faq_q6": {
        "ko": "오프라인에서도 사용할 수 있나요?",
        "en": "Can I use it offline?",
        "vi": "Có thể sử dụng ngoại tuyến không?",
        "zh": "可以离线使用吗？",
    },
    "faq_a6": {
        "ko": "네. 한번 수집된 데이터는 로컬 데이터베이스에 저장되므로, 인터넷 연결 없이도 이전에 수집한 정보를 확인할 수 있습니다.",
        "en": "Yes. Collected data is stored in a local database, so you can view previously collected information without internet.",
        "vi": "Có. Dữ liệu đã thu thập được lưu trong cơ sở dữ liệu cục bộ, bạn có thể xem mà không cần internet.",
        "zh": "可以。收集的数据保存在本地数据库中，无需互联网即可查看已收集的信息。",
    },
    "contacts_section": {
        "ko": "📞 주요 연락처",
        "en": "📞 Key Contacts",
        "vi": "📞 Liên hệ chính",
        "zh": "📞 主要联系方式",
    },
    "contact_danuri": {
        "ko": "다누리 콜센터",
        "en": "Danuri Call Center",
        "vi": "Tổng đài Danuri",
        "zh": "多元文化呼叫中心",
    },
    "contact_danuri_desc": {
        "ko": "다문화가족 상담 (13개 언어 지원)",
        "en": "Multicultural family counseling (13 languages)",
        "vi": "Tư vấn gia đình đa văn hóa (13 ngôn ngữ)",
        "zh": "多文化家庭咨询（支持13种语言）",
    },
    "contact_foreigner": {
        "ko": "외국인종합안내센터",
        "en": "Foreigner Information Center",
        "vi": "Trung tâm Thông tin Người nước ngoài",
        "zh": "外国人综合咨询中心",
    },
    "contact_foreigner_desc": {
        "ko": "출입국·체류·비자 상담",
        "en": "Immigration, stay, and visa consultation",
        "vi": "Tư vấn xuất nhập cảnh, cư trú, visa",
        "zh": "出入境·居留·签证咨询",
    },
    "contact_gov": {
        "ko": "정부민원안내",
        "en": "Government Helpline",
        "vi": "Đường dây Chính phủ",
        "zh": "政府民愿咨询",
    },
    "contact_gov_desc": {
        "ko": "정부 서비스 전반 안내",
        "en": "General government service guidance",
        "vi": "Hướng dẫn dịch vụ chính phủ",
        "zh": "政府服务综合咨询",
    },
    "contact_labor": {
        "ko": "고용노동부",
        "en": "Ministry of Employment and Labor",
        "vi": "Bộ Việc làm và Lao động",
        "zh": "雇佣劳动部",
    },
    "contact_labor_desc": {
        "ko": "외국인 근로자 고용·노동 상담",
        "en": "Foreign worker employment and labor consultation",
        "vi": "Tư vấn việc làm và lao động cho người nước ngoài",
        "zh": "外国人劳动者雇佣·劳动咨询",
    },
    "app_info_section": {
        "ko": "ℹ️ 앱 정보",
        "en": "ℹ️ App Info",
        "vi": "ℹ️ Thông tin ứng dụng",
        "zh": "ℹ️ 应用信息",
    },
    "app_version": {
        "ko": "다문화 정보 허브 v0.1.0",
        "en": "Multicultural Info Hub v0.1.0",
        "vi": "Trung tâm Thông tin Đa văn hóa v0.1.0",
        "zh": "多文化信息中心 v0.1.0",
    },
    "app_data_source": {
        "ko": "데이터 출처: 법제처 Open API, 공공데이터포털, RSS 피드",
        "en": "Data sources: Legislation API, Public Data Portal, RSS feeds",
        "vi": "Nguồn dữ liệu: API Luật pháp, Cổng Dữ liệu Công khai, RSS",
        "zh": "数据来源：法制处API、公共数据门户、RSS源",
    },

    # -- 생활영역 뷰 제목/설명 --
    "visa_title": {
        "ko": "비자·체류",
        "en": "Visa & Residency",
        "vi": "Visa & Cư trú",
        "zh": "签证·居留",
    },
    "visa_desc": {
        "ko": "출입국 정책, 비자 제도, 체류 자격 변경, 귀화·국적 관련 정보를 모아봅니다.",
        "en": "Immigration policy, visa system, residency status changes, and naturalization information.",
        "vi": "Chính sách xuất nhập cảnh, hệ thống visa, thay đổi tư cách cư trú và quốc tịch.",
        "zh": "出入境政策、签证制度、居留资格变更、归化·国籍相关信息。",
    },
    "health_title": {
        "ko": "의료·복지",
        "en": "Health & Welfare",
        "vi": "Y tế & Phúc lợi",
        "zh": "医疗·福利",
    },
    "health_desc": {
        "ko": "의료비 지원, 건강검진, 의료 통역, 복지 서비스 관련 정보를 모아봅니다.",
        "en": "Medical expense support, health checkups, medical interpretation, and welfare services.",
        "vi": "Hỗ trợ chi phí y tế, khám sức khỏe, phiên dịch y tế và dịch vụ phúc lợi.",
        "zh": "医疗费支援、健康检查、医疗翻译、福利服务相关信息。",
    },
    "family_title": {
        "ko": "가족·육아",
        "en": "Family & Childcare",
        "vi": "Gia đình & Chăm sóc trẻ",
        "zh": "家庭·育儿",
    },
    "family_desc": {
        "ko": "다문화가족 방문교육, 이중언어 환경, 자녀 교육 관련 정보를 모아봅니다.",
        "en": "Home visit education, bilingual environment, and child education for multicultural families.",
        "vi": "Giáo dục tại nhà, môi trường song ngữ và giáo dục con em gia đình đa văn hóa.",
        "zh": "多文化家庭访问教育、双语环境、子女教育相关信息。",
    },
    "education_title": {
        "ko": "교육·문화",
        "en": "Education & Culture",
        "vi": "Giáo dục & Văn hóa",
        "zh": "教育·文化",
    },
    "education_desc": {
        "ko": "한국어 교육, 문화 프로그램, 사회통합프로그램(KIIP) 관련 정보를 모아봅니다.",
        "en": "Korean language education, cultural programs, and KIIP (Social Integration Program) information.",
        "vi": "Giáo dục tiếng Hàn, chương trình văn hóa và chương trình Hội nhập Xã hội (KIIP).",
        "zh": "韩国语教育、文化项目、社会统合项目（KIIP）相关信息。",
    },
    "job_title": {
        "ko": "일자리",
        "en": "Jobs & Employment",
        "vi": "Việc làm",
        "zh": "就业",
    },
    "job_desc": {
        "ko": "취업 연계, 직업 교육, 자격증 지원, 외국인 고용 관련 정보를 모아봅니다.",
        "en": "Job placement, vocational training, certification support, and foreign worker employment.",
        "vi": "Kết nối việc làm, đào tạo nghề, hỗ trợ chứng chỉ và việc làm cho người nước ngoài.",
        "zh": "就业连接、职业教育、资格证支援、外国人雇佣相关信息。",
    },
    "amended": {
        "ko": "개정",
        "en": "Amended",
        "vi": "Sửa đổi",
        "zh": "修订",
    },
    "effective": {
        "ko": "시행",
        "en": "Effective",
        "vi": "Có hiệu lực",
        "zh": "施行",
    },
    "deadline_label": {
        "ko": "마감",
        "en": "Deadline",
        "vi": "Hạn chót",
        "zh": "截止",
    },

    # -- 메인 윈도우 / 트레이 --
    "tray_open": {
        "ko": "열기",
        "en": "Open",
        "vi": "Mở",
        "zh": "打开",
    },
    "tray_update": {
        "ko": "지금 업데이트",
        "en": "Update Now",
        "vi": "Cập nhật ngay",
        "zh": "立即更新",
    },
    "tray_quit": {
        "ko": "종료",
        "en": "Quit",
        "vi": "Thoát",
        "zh": "退出",
    },
    "data_refresh_tooltip": {
        "ko": "데이터 새로고침",
        "en": "Refresh data",
        "vi": "Làm mới dữ liệu",
        "zh": "刷新数据",
    },
    "manual_collection_start": {
        "ko": "수동 수집 시작...",
        "en": "Starting manual collection...",
        "vi": "Bắt đầu thu thập thủ công...",
        "zh": "开始手动采集...",
    },
    "view_refreshed": {
        "ko": "뷰 갱신 완료",
        "en": "Views refreshed",
        "vi": "Đã làm mới giao diện",
        "zh": "视图已刷新",
    },
    "export_done": {
        "ko": "내보내기 완료",
        "en": "Export complete",
        "vi": "Xuất hoàn tất",
        "zh": "导出完成",
    },
    "export_failed": {
        "ko": "내보내기 실패",
        "en": "Export failed",
        "vi": "Xuất thất bại",
        "zh": "导出失败",
    },
    "notify_news_title": {
        "ko": "새 뉴스",
        "en": "New News",
        "vi": "Tin mới",
        "zh": "新消息",
    },
    "notify_news_msg": {
        "ko": "뉴스 {count}건이 수집되었습니다.",
        "en": "{count} news articles collected.",
        "vi": "Đã thu thập {count} tin tức.",
        "zh": "已收集{count}条新闻。",
    },
    "notify_law_title": {
        "ko": "법령 업데이트",
        "en": "Law Update",
        "vi": "Cập nhật luật",
        "zh": "法令更新",
    },
    "notify_law_msg": {
        "ko": "법령 {count}건이 수집되었습니다.",
        "en": "{count} laws collected.",
        "vi": "Đã thu thập {count} luật.",
        "zh": "已收集{count}条法令。",
    },
    "notify_support_title": {
        "ko": "지원사업 업데이트",
        "en": "Program Update",
        "vi": "Cập nhật chương trình",
        "zh": "支援事业更新",
    },
    "notify_support_msg": {
        "ko": "지원사업 {count}건이 수집되었습니다.",
        "en": "{count} programs collected.",
        "vi": "Đã thu thập {count} chương trình.",
        "zh": "已收集{count}个支援事业。",
    },
    "notify_all_title": {
        "ko": "데이터 수집 완료",
        "en": "Data Collection Complete",
        "vi": "Thu thập dữ liệu hoàn tất",
        "zh": "数据采集完成",
    },
    "collection_status": {
        "ko": "수집 완료 — 뉴스 {news}, 법령 {laws}, 지원사업 {support} (총 {total}건)",
        "en": "Collection done — News {news}, Laws {laws}, Programs {support} (Total {total})",
        "vi": "Thu thập xong — Tin {news}, Luật {laws}, Chương trình {support} (Tổng {total})",
        "zh": "采集完成 — 新闻{news}、法令{laws}、支援事业{support}（共{total}条）",
    },
    "news_collected_status": {
        "ko": "뉴스 {count}건 수집 완료",
        "en": "Collected {count} news articles",
        "vi": "Đã thu thập {count} tin tức",
        "zh": "已收集{count}条新闻",
    },
    "laws_collected_status": {
        "ko": "법령 {count}건 수집 완료",
        "en": "Collected {count} laws",
        "vi": "Đã thu thập {count} luật",
        "zh": "已收集{count}条法令",
    },
    "support_collected_status": {
        "ko": "지원사업 {count}건 수집 완료",
        "en": "Collected {count} programs",
        "vi": "Đã thu thập {count} chương trình",
        "zh": "已收集{count}个支援事业",
    },
    "error_prefix": {
        "ko": "오류",
        "en": "Error",
        "vi": "Lỗi",
        "zh": "错误",
    },
    "file_saved": {
        "ko": "파일 저장",
        "en": "File saved",
        "vi": "Đã lưu tệp",
        "zh": "文件已保存",
    },

    # -- 키워드 관리 다이얼로그 --
    "keyword_desc": {
        "ko": "관심 키워드를 등록하면 새 뉴스/지원사업에 해당 키워드가 포함될 때 알림을 받습니다.",
        "en": "Register keywords to get notified when new news or programs contain them.",
        "vi": "Đăng ký từ khóa để nhận thông báo khi có tin tức hoặc chương trình mới chứa từ khóa.",
        "zh": "注册关键词，当新消息或支援事业包含关键词时将收到通知。",
    },
    "keyword_placeholder": {
        "ko": "키워드 입력...",
        "en": "Enter keyword...",
        "vi": "Nhập từ khóa...",
        "zh": "输入关键词...",
    },
    "keyword_add": {
        "ko": "추가",
        "en": "Add",
        "vi": "Thêm",
        "zh": "添加",
    },
    "keyword_delete": {
        "ko": "삭제",
        "en": "Delete",
        "vi": "Xóa",
        "zh": "删除",
    },
    "keyword_exists": {
        "ko": "이미 등록된 키워드입니다.",
        "en": "This keyword already exists.",
        "vi": "Từ khóa này đã tồn tại.",
        "zh": "该关键词已存在。",
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
