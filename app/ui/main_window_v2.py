"""
다문화 정보 허브 — 메인 윈도우 v2
디자인: 다누리(danuri.go.kr) 참고 — 생활영역별 분류
레이아웃: 라이트 사이드바(앱명 + 생활영역 그룹) + 콘텐츠 영역

※ 개발 검토용 버전 — 기존 main_window.py는 그대로 유지됨
   채택 결정 시 main_window.py로 복사하여 사용
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


# ------------------------------------------------------------------
# 메뉴 구조: 생활영역별 분류 (다누리 방식)
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

_ALL_KEYS: list[str] = (
    [item[2] for g in _MENU_GROUPS for item in g["items"]]
    + [item[2] for item in _BOTTOM_ITEMS]
)


# ------------------------------------------------------------------
# 색상 상수 (Notion/Linear 라이트 + 다누리 포인트 컬러)
# ------------------------------------------------------------------
C_SIDEBAR_BG    = "#F8F9FA"
C_SIDEBAR_BOR   = "#E8EAED"
C_ITEM_DEFAULT  = "transparent"
C_ITEM_HOVER    = "#EAECF0"
C_ITEM_ACTIVE   = "#E8F0FE"
C_ITEM_TEXT     = "#202124"
C_ITEM_ACTIVE_T = "#1A73E8"      # Google Material Blue (다누리 계열)
C_SECTION_LBL   = "#80868B"
C_CONTENT_BG    = "#FFFFFF"
C_DIVIDER       = "#E8EAED"
C_STATUS_BG     = "#F8F9FA"


class NavButton(QPushButton):
    """사이드바 메뉴 버튼."""

    def __init__(self, icon: str, label: str, indent: bool = False, parent=None) -> None:
        super().__init__(f"  {icon}  {label}", parent)
        self._indent = indent
        self._active = False
        self.setFixedHeight(32)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._refresh_style()

    def set_active(self, active: bool) -> None:
        if self._active == active:
            return
        self._active = active
        self._refresh_style()

    def _refresh_style(self) -> None:
        indent_pad = "22px" if self._indent else "10px"
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 5px 12px 5px {indent_pad};
                    border: none;
                    border-left: 3px solid {C_ITEM_ACTIVE_T};
                    border-radius: 0px;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    background: {C_ITEM_ACTIVE};
                    color: {C_ITEM_ACTIVE_T};
                    font-weight: 600;
                    font-size: 13px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 5px 12px 5px {indent_pad};
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
class MainWindowV2(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._nav_buttons: dict[str, NavButton] = {}
        self._current_key: str | None = None

        self._setup_window()
        self._build_ui()
        self._navigate_to("dashboard")

    def _setup_window(self) -> None:
        self.setWindowTitle(f"{self._config.name} v2")
        self.resize(self._config.window_width, self._config.window_height)
        self.setMinimumSize(QSize(960, 640))
        font = QFont("Segoe UI", self._config.font_size)
        self.setFont(font)
        self.setStyleSheet(f"QMainWindow {{ background: {C_CONTENT_BG}; }}")

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
            f"QStatusBar {{ background: {C_STATUS_BG}; color: #80868B; "
            f"font-size: 11px; border-top: 1px solid {C_DIVIDER}; }}"
        )
        self._status_bar.showMessage("준비")
        self.setStatusBar(self._status_bar)

    # ------------------------------------------------------------------
    # 사이드바
    # ------------------------------------------------------------------
    def _build_sidebar(self) -> QWidget:
        outer = QWidget()
        outer.setFixedWidth(230)
        outer.setStyleSheet(
            f"background: {C_SIDEBAR_BG}; "
            f"border-right: 1px solid {C_SIDEBAR_BOR};"
        )

        layout = QVBoxLayout(outer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── 브랜드 영역 ────────────────────────────────────────────
        brand = QWidget()
        brand.setFixedHeight(56)
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(16, 0, 16, 0)
        brand_layout.setSpacing(8)

        icon_lbl = QLabel("🌏")
        icon_lbl.setStyleSheet("font-size: 22px;")
        name_lbl = QLabel(self._config.name)
        name_lbl.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #202124; letter-spacing: -0.2px;"
        )
        brand_layout.addWidget(icon_lbl)
        brand_layout.addWidget(name_lbl)
        brand_layout.addStretch()
        layout.addWidget(brand)
        layout.addWidget(self._divider())

        # ── 스크롤 가능한 메뉴 영역 ────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")

        menu_widget = QWidget()
        menu_widget.setStyleSheet("background: transparent;")
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(8, 8, 8, 8)
        menu_layout.setSpacing(1)

        for group in _MENU_GROUPS:
            if group["label"]:
                sep = QLabel(group["label"].upper())
                sep.setStyleSheet(
                    f"color: {C_SECTION_LBL}; font-size: 10px; font-weight: 700; "
                    "letter-spacing: 0.8px; padding: 12px 8px 4px 8px;"
                )
                menu_layout.addWidget(sep)

            is_sub = group["label"] is not None  # 홈 제외 들여쓰기
            for icon, label, key in group["items"]:
                btn = NavButton(icon, label, indent=is_sub)
                btn.clicked.connect(lambda _, k=key: self._navigate_to(k))
                self._nav_buttons[key] = btn
                menu_layout.addWidget(btn)

        menu_layout.addStretch()
        scroll.setWidget(menu_widget)
        layout.addWidget(scroll, 1)

        # ── 하단 고정 ──────────────────────────────────────────────
        layout.addWidget(self._divider())

        bottom = QWidget()
        bottom.setStyleSheet("background: transparent;")
        btm_layout = QVBoxLayout(bottom)
        btm_layout.setContentsMargins(8, 6, 8, 6)
        btm_layout.setSpacing(1)

        for icon, label, key in _BOTTOM_ITEMS:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda _, k=key: self._navigate_to(k))
            self._nav_buttons[key] = btn
            btm_layout.addWidget(btn)

        layout.addWidget(bottom)

        # ── 언어 선택 ──────────────────────────────────────────────
        layout.addWidget(self._divider())

        lang_area = QWidget()
        lang_area.setStyleSheet("background: transparent;")
        lang_layout = QHBoxLayout(lang_area)
        lang_layout.setContentsMargins(12, 8, 12, 12)

        self._lang_btn = QPushButton("🌐 한국어")
        self._lang_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ITEM_DEFAULT};
                border: 1px solid {C_DIVIDER};
                border-radius: 6px;
                padding: 5px 10px;
                color: #5F6368;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: {C_ITEM_HOVER}; }}
        """)
        self._lang_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lang_layout.addWidget(self._lang_btn)
        layout.addWidget(lang_area)

        return outer

    # ------------------------------------------------------------------
    # 콘텐츠 영역
    # ------------------------------------------------------------------
    def _build_main_area(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {C_CONTENT_BG};")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {C_CONTENT_BG};")

        # 뷰 이름 맵 (key → 표시 이름)
        label_map: dict[str, str] = {}
        for g in _MENU_GROUPS:
            for icon, label, key in g["items"]:
                label_map[key] = f"{icon} {label}"
        for icon, label, key in _BOTTOM_ITEMS:
            label_map[key] = f"{icon} {label}"

        for key in _ALL_KEYS:
            placeholder = QLabel(f"{label_map.get(key, key)}\n\n준비 중입니다")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet(
                "color: #BDC1C6; font-size: 16px; line-height: 1.8;"
            )
            placeholder.setObjectName(f"view_{key}")
            self._stack.addWidget(placeholder)

        layout.addWidget(self._stack)
        return container

    # ------------------------------------------------------------------
    # 헬퍼 / 내비게이션
    # ------------------------------------------------------------------
    def _divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        return line

    def _navigate_to(self, key: str) -> None:
        if key not in _ALL_KEYS:
            return
        if self._current_key and self._current_key in self._nav_buttons:
            self._nav_buttons[self._current_key].set_active(False)
        if key in self._nav_buttons:
            self._nav_buttons[key].set_active(True)
        self._current_key = key
        self._stack.setCurrentIndex(_ALL_KEYS.index(key))

    def update_status(self, message: str) -> None:
        self._status_bar.showMessage(message)
