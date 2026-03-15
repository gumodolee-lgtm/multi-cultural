"""뷰 모듈"""
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.news_view import NewsView
from app.ui.views.law_view import LawView
from app.ui.views.support_view import SupportView
from app.ui.views.search_view import SearchView
from app.ui.views.bookmark_view import BookmarkView
from app.ui.views.settings_view import SettingsView
from app.ui.views.help_view import HelpView
from app.ui.views.life_area_view import (
    VisaAreaView, HealthAreaView, FamilyAreaView,
    EducationAreaView, JobAreaView,
)

__all__ = [
    "DashboardView", "NewsView", "LawView", "SupportView",
    "SearchView", "BookmarkView", "SettingsView", "HelpView",
    "VisaAreaView", "HealthAreaView", "FamilyAreaView",
    "EducationAreaView", "JobAreaView",
]
