"""뷰 모듈"""
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.news_view import NewsView
from app.ui.views.law_view import LawView
from app.ui.views.support_view import SupportView
from app.ui.views.search_view import SearchView
from app.ui.views.bookmark_view import BookmarkView
from app.ui.views.settings_view import SettingsView

__all__ = [
    "DashboardView", "NewsView", "LawView", "SupportView",
    "SearchView", "BookmarkView", "SettingsView",
]
