"""
다문화 정보 허브 — 메인 윈도우
디자인: Notion/Linear 스타일 라이트 사이드바
레이아웃: 사이드바(앱명 + 그룹 메뉴) + 콘텐츠 영역
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QStatusBar,
    QFrame, QSizePolicy, QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QCursor

from app.utils.config_loader import AppConfig
from app.ui.views import (
    DashboardView, NewsView, LawView, SupportView,
    SearchView, BookmarkView, SettingsView,
)


# ------------------------------------------------------------------
# 메뉴 구조 정의 — 안 A: 생활영역별 (다누리 방식)
# ------------------------------------------------------------------
_MENU_GROUPS = [
    {
        "label": None,
        "items": [
            ("🏠", "홈", "dashboard"),
        ],
    },
    {
        "label": "생활 영역",
        "items": [
            ("🛂", "비자·체류", "visa"),
            ("⚕️",  "의료·복지", "health"),
            ("👶", "가족·육아", "family"),
            ("🎓", "교육·문화", "education"),
            ("💼", "일자리", "job"),
        ],
    },
    {
        "label": "정보",
        "items": [
            ("📰", "뉴스·공지", "news"),
            ("⚖️",  "법령·규정", "law"),
            ("🏛️", "지원사업", "support"),
        ],
    },
    {
        "label": "도구",
        "items": [
            ("🔍", "통합 검색", "search"),
            ("⭐", "즐겨찾기", "bookmark"),
        ],
    },
]

_BOTTOM_ITEMS = [
    ("⚙️", "설정", "settings"),
    ("❓", "도움말", "help"),
]

# 전체 메뉴 키 목록 (순서 보장)
_ALL_KEYS: list[str] = (
    [item[2] for g in _MENU_GROUPS for item in g["items"]]
    + [item[2] for item in _BOTTOM_ITEMS]
)


# ------------------------------------------------------------------
# 색상 / 스타일 상수
# ------------------------------------------------------------------
C_SIDEBAR_BG   = "#F7F7F7"
C_SIDEBAR_BOR  = "#E5E5E5"
C_ITEM_DEFAULT = "transparent"
C_ITEM_HOVER   = "#EBEBEB"
C_ITEM_ACTIVE  = "#E3EAF6"
C_ITEM_TEXT    = "#1A1A1A"
C_ITEM_ACTIVE_T = "#1558D6"
C_SECTION_LABEL = "#9E9E9E"
C_CONTENT_BG   = "#FFFFFF"
C_HEADER_BG    = "#FFFFFF"
C_HEADER_BOR   = "#EEEEEE"
C_DIVIDER      = "#E5E5E5"

_BTN_STYLE = """
    QPushButton {{
        text-align: left;
        padding: 6px 14px 6px 14px;
        border: none;
        border-radius: 6px;
        background: {bg};
        color: {fg};
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: {hover};
    }}
"""


class NavButton(QPushButton):
    """사이드바 메뉴 버튼 — active/inactive 상태 전환 지원."""

    def __init__(self, icon: str, label: str, parent=None) -> None:
        super().__init__(f"  {icon}  {label}", parent)
        self.setFixedHeight(34)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._active = False
        self._refresh_style()

    def set_active(self, active: bool) -> None:
        if self._active == active:
            return
        self._active = active
        self._refresh_style()

    def _refresh_style(self) -> None:
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 6px 14px 6px 10px;
                    border: none;
                    border-left: 3px solid {C_ITEM_ACTIVE_T};
                    border-radius: 0px;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    background: {C_ITEM_ACTIVE};
                    color: {C_ITEM_ACTIVE_T};
                    font-weight: bold;
                    font-size: 13px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 6px 14px 6px 13px;
                    border: none;
                    border-radius: 6px;
                    background: {C_ITEM_DEFAULT};
                    color: {C_ITEM_TEXT};
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {C_ITEM_HOVER};
                }}
            """)


# ------------------------------------------------------------------
# 메인 윈도우
# ------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._nav_buttons: dict[str, NavButton] = {}
        self._current_key: str | None = None

        self._setup_window()
        self._build_ui()
        self._navigate_to("dashboard")

    # ------------------------------------------------------------------
    def _setup_window(self) -> None:
        self.setWindowTitle(self._config.name)
        self.resize(self._config.window_width, self._config.window_height)
        self.setMinimumSize(QSize(900, 600))

        font = QFont("Segoe UI", self._config.font_size)
        self.setFont(font)
        self.setStyleSheet(f"QMainWindow {{ background: {C_CONTENT_BG}; }}")

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_main_area())

        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(
            f"QStatusBar {{ background: {C_HEADER_BG}; color: #888; font-size: 11px; "
            f"border-top: 1px solid {C_HEADER_BOR}; }}"
        )
        self._status_bar.showMessage("준비")
        self.setStatusBar(self._status_bar)

    # ------------------------------------------------------------------
    # 사이드바
    # ------------------------------------------------------------------
    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            f"QWidget {{ background: {C_SIDEBAR_BG}; }}"
            f"QWidget#sidebar {{ border-right: 1px solid {C_SIDEBAR_BOR}; }}"
        )
        sidebar.setObjectName("sidebar")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── 앱 브랜드 ──────────────────────────────────────────────
        brand = QWidget()
        brand.setFixedHeight(52)
        brand.setStyleSheet(f"background: {C_SIDEBAR_BG};")
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(16, 0, 16, 0)

        app_icon = QLabel("🌏")
        app_icon.setStyleSheet("font-size: 20px;")
        app_name = QLabel(self._config.name)
        app_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A1A1A;")

        brand_layout.addWidget(app_icon)
        brand_layout.addWidget(app_name)
        brand_layout.addStretch()
        layout.addWidget(brand)

        # 구분선
        layout.addWidget(self._make_divider())

        # ── 메뉴 그룹 (스크롤 가능) ────────────────────────────────
        menu_widget = QWidget()
        menu_widget.setStyleSheet("background: transparent;")
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(8, 8, 8, 8)
        menu_layout.setSpacing(1)

        for group in _MENU_GROUPS:
            if group["label"]:
                section_label = QLabel(group["label"].upper())
                section_label.setStyleSheet(
                    f"color: {C_SECTION_LABEL}; font-size: 10px; "
                    "font-weight: bold; letter-spacing: 0.8px;"
                    "padding: 12px 8px 4px 8px;"
                )
                menu_layout.addWidget(section_label)

            for icon, label, key in group["items"]:
                btn = NavButton(icon, label)
                btn.clicked.connect(lambda _, k=key: self._navigate_to(k))
                self._nav_buttons[key] = btn
                menu_layout.addWidget(btn)

        menu_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(menu_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")
        layout.addWidget(scroll, 1)

        # ── 하단 고정 (설정·도움말) ────────────────────────────────
        layout.addWidget(self._make_divider())

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(8, 6, 8, 12)
        bottom_layout.setSpacing(2)

        for icon, label, key in _BOTTOM_ITEMS:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda _, k=key: self._navigate_to(k))
            self._nav_buttons[key] = btn
            bottom_layout.addWidget(btn)

        layout.addWidget(bottom_widget)

        # ── 사용자 언어 버튼 ───────────────────────────────────────
        lang_widget = QWidget()
        lang_widget.setStyleSheet(
            f"background: {C_SIDEBAR_BG}; border-top: 1px solid {C_DIVIDER};"
        )
        lang_layout = QHBoxLayout(lang_widget)
        lang_layout.setContentsMargins(12, 8, 12, 12)

        self._lang_btn = QPushButton("🌐 한국어")
        self._lang_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ITEM_DEFAULT};
                border: 1px solid {C_DIVIDER};
                border-radius: 6px;
                padding: 5px 10px;
                color: #555;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: {C_ITEM_HOVER}; }}
        """)
        lang_layout.addWidget(self._lang_btn)
        layout.addWidget(lang_widget)

        return sidebar

    # ------------------------------------------------------------------
    # 메인 영역 (콘텐츠)
    # ------------------------------------------------------------------
    def _build_main_area(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {C_CONTENT_BG};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {C_CONTENT_BG};")

        # 뷰 매핑: key → 실제 뷰 위젯 (없으면 플레이스홀더)
        _view_map = {
            "dashboard": DashboardView,
            "news": NewsView,
            "law": LawView,
            "support": SupportView,
            "search": SearchView,
            "bookmark": BookmarkView,
            "settings": SettingsView,
        }

        for key in _ALL_KEYS:
            view_cls = _view_map.get(key)
            if view_cls:
                view = view_cls()
            else:
                label_text = next(
                    (item[1] for g in _MENU_GROUPS for item in g["items"] if item[2] == key),
                    next((item[1] for item in _BOTTOM_ITEMS if item[2] == key), key),
                )
                view = QLabel(f"{label_text} (준비 중)")
                view.setAlignment(Qt.AlignmentFlag.AlignCenter)
                view.setStyleSheet("color: #BDBDBD; font-size: 18px;")
            view.setObjectName(f"view_{key}")
            self._stack.addWidget(view)

        layout.addWidget(self._stack)
        return container

    # ------------------------------------------------------------------
    # 헬퍼
    # ------------------------------------------------------------------
    def _make_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        return line

    # ------------------------------------------------------------------
    # 내비게이션
    # ------------------------------------------------------------------
    def _navigate_to(self, key: str) -> None:
        if key not in _ALL_KEYS:
            return

        # 이전 버튼 비활성화
        if self._current_key and self._current_key in self._nav_buttons:
            self._nav_buttons[self._current_key].set_active(False)

        # 새 버튼 활성화
        if key in self._nav_buttons:
            self._nav_buttons[key].set_active(True)

        self._current_key = key
        self._stack.setCurrentIndex(_ALL_KEYS.index(key))

    def update_status(self, message: str) -> None:
        self._status_bar.showMessage(message)
