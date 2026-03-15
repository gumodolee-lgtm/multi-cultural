"""
다문화 정보 허브 — 메인 윈도우
디자인: Notion/Linear 스타일 라이트 사이드바
레이아웃: 사이드바(앱명 + 그룹 메뉴) + 콘텐츠 영역
"""
from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QStatusBar,
    QFrame, QSizePolicy, QScrollArea,
    QSystemTrayIcon, QMenu,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QCursor, QIcon, QPixmap, QPainter, QColor

from app.utils.config_loader import AppConfig
from app.utils.i18n import tr, set_language, get_language, get_supported_languages
from app.ui.signals import CollectionSignal
from app.ui.views import (
    DashboardView, NewsView, LawView, SupportView,
    SearchView, BookmarkView, SettingsView, HelpView,
    VisaAreaView, HealthAreaView, FamilyAreaView,
    EducationAreaView, JobAreaView,
)

if TYPE_CHECKING:
    from app.scheduler.scheduler import CollectorScheduler

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# 메뉴 구조 정의 — (icon, i18n_key, nav_key)
# label은 i18n 키로 관리 (None = 그룹 헤더 없음)
# ------------------------------------------------------------------
_MENU_GROUPS = [
    {
        "label_key": None,
        "items": [
            ("🏠", "home", "dashboard"),
        ],
    },
    {
        "label_key": "life_areas",
        "items": [
            ("🛂", "visa", "visa"),
            ("⚕️",  "health", "health"),
            ("👶", "family", "family"),
            ("🎓", "education", "education"),
            ("💼", "job", "job"),
        ],
    },
    {
        "label_key": "information",
        "items": [
            ("📰", "news", "news"),
            ("⚖️",  "law", "law"),
            ("🏛️", "support", "support"),
        ],
    },
    {
        "label_key": "tools",
        "items": [
            ("🔍", "search", "search"),
            ("⭐", "bookmark", "bookmark"),
        ],
    },
]

_BOTTOM_ITEMS = [
    ("⚙️", "settings", "settings"),
    ("❓", "help", "help"),
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
        self._scheduler: CollectorScheduler | None = None

        # 시그널 객체 — 스케줄러와 공유
        self.collection_signal = CollectionSignal()

        self._setup_window()
        self._build_ui()
        self._setup_tray()
        self._connect_signals()
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
    # 시그널 연결
    # ------------------------------------------------------------------
    def _connect_signals(self) -> None:
        """수집 완료 시그널 → 뷰 갱신 + 상태바 업데이트."""
        sig = self.collection_signal
        sig.news_collected.connect(self._on_news_collected)
        sig.laws_collected.connect(self._on_laws_collected)
        sig.support_collected.connect(self._on_support_collected)
        sig.all_collected.connect(self._on_all_collected)
        sig.error_occurred.connect(self._on_error)

    def _on_news_collected(self, count: int) -> None:
        self.update_status(f"뉴스 {count}건 수집 완료")
        self._refresh_all_views()
        if count > 0:
            self._tray_notify("새 뉴스", f"뉴스 {count}건이 수집되었습니다.")

    def _on_laws_collected(self, count: int) -> None:
        self.update_status(f"법령 {count}건 수집 완료")
        self._refresh_all_views()
        if count > 0:
            self._tray_notify("법령 업데이트", f"법령 {count}건이 수집되었습니다.")

    def _on_support_collected(self, count: int) -> None:
        self.update_status(f"지원사업 {count}건 수집 완료")
        self._refresh_all_views()
        if count > 0:
            self._tray_notify("지원사업 업데이트", f"지원사업 {count}건이 수집되었습니다.")

    def _on_all_collected(self, news: int, laws: int, support: int) -> None:
        total = news + laws + support
        self.update_status(
            f"수집 완료 — 뉴스 {news}, 법령 {laws}, 지원사업 {support} (총 {total}건)"
        )
        self._refresh_all_views()
        if total > 0:
            self._tray_notify(
                "데이터 수집 완료",
                f"뉴스 {news}건, 법령 {laws}건, 지원사업 {support}건",
            )

    def _on_error(self, message: str) -> None:
        self.update_status(f"오류: {message}")
        logger.warning("수집 오류 시그널: %s", message)

    def _refresh_all_views(self) -> None:
        """refresh_data() 메서드가 있는 모든 뷰를 갱신한다."""
        for i in range(self._stack.count()):
            widget = self._stack.widget(i)
            if hasattr(widget, "refresh_data"):
                try:
                    widget.refresh_data()
                except Exception:
                    logger.exception("뷰 갱신 실패: %s", widget.objectName())

    # ------------------------------------------------------------------
    # 시스템 트레이
    # ------------------------------------------------------------------
    def _setup_tray(self) -> None:
        """시스템 트레이 아이콘 및 메뉴를 설정한다."""
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(self._create_app_icon())
        self._tray_icon.setToolTip(self._config.name)

        # 트레이 메뉴
        tray_menu = QMenu()
        show_action = tray_menu.addAction("열기")
        show_action.triggered.connect(self._show_from_tray)

        refresh_action = tray_menu.addAction("지금 업데이트")
        refresh_action.triggered.connect(self._manual_refresh)

        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("종료")
        quit_action.triggered.connect(self.close)

        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_tray_activated)
        self._tray_icon.show()

    def _create_app_icon(self) -> QIcon:
        """간단한 원형 앱 아이콘을 프로그래밍으로 생성한다."""
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 파란 원
        painter.setBrush(QColor("#1565C0"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, size - 8, size - 8)

        # 흰색 'M' 텍스트
        painter.setPen(QColor("white"))
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "M")

        painter.end()
        return QIcon(pixmap)

    def _tray_notify(self, title: str, message: str) -> None:
        """시스템 트레이 토스트 알림을 표시한다."""
        if self._tray_icon.isSystemTrayAvailable():
            self._tray_icon.showMessage(
                title, message,
                QSystemTrayIcon.MessageIcon.Information,
                5000,
            )

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self) -> None:
        """트레이에서 창을 복원한다."""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    # ------------------------------------------------------------------
    # 스케줄러 연동
    # ------------------------------------------------------------------
    def set_scheduler(self, scheduler: CollectorScheduler) -> None:
        """스케줄러 참조를 저장한다 (수동 새로고침용)."""
        self._scheduler = scheduler

    def _manual_refresh(self) -> None:
        """사용자가 수동으로 데이터를 새로고침한다."""
        self.update_status("수동 수집 시작...")
        if self._scheduler:
            t = threading.Thread(target=self._scheduler.run_once, daemon=True)
            t.start()
        else:
            self._refresh_all_views()
            self.update_status("뷰 갱신 완료")

    def _export_data(self) -> None:
        """데이터를 Excel 파일로 내보낸다."""
        from app.services.export_service import ExportService
        try:
            path = ExportService.export_all()
            self.update_status(f"내보내기 완료: {path}")
            self._tray_notify("내보내기 완료", f"파일 저장: {path}")
        except Exception as e:
            self.update_status(f"내보내기 실패: {e}")
            logger.exception("내보내기 실패")

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
        self._app_name_label = QLabel(tr("app_name"))
        self._app_name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A1A1A;")

        brand_layout.addWidget(app_icon)
        brand_layout.addWidget(self._app_name_label)
        brand_layout.addStretch()

        # 새로고침 버튼
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        refresh_btn.setToolTip("데이터 새로고침")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {C_ITEM_HOVER};
            }}
        """)
        refresh_btn.clicked.connect(self._manual_refresh)
        brand_layout.addWidget(refresh_btn)

        layout.addWidget(brand)

        # 구분선
        layout.addWidget(self._make_divider())

        # ── 메뉴 그룹 (스크롤 가능) ────────────────────────────────
        menu_widget = QWidget()
        menu_widget.setStyleSheet("background: transparent;")
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(8, 8, 8, 8)
        menu_layout.setSpacing(1)

        self._section_labels: list[tuple[str, QLabel]] = []  # (i18n_key, widget)

        for group in _MENU_GROUPS:
            if group["label_key"]:
                section_label = QLabel(tr(group["label_key"]).upper())
                section_label.setStyleSheet(
                    f"color: {C_SECTION_LABEL}; font-size: 10px; "
                    "font-weight: bold; letter-spacing: 0.8px;"
                    "padding: 12px 8px 4px 8px;"
                )
                self._section_labels.append((group["label_key"], section_label))
                menu_layout.addWidget(section_label)

            for icon, i18n_key, key in group["items"]:
                btn = NavButton(icon, tr(i18n_key))
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

        for icon, i18n_key, key in _BOTTOM_ITEMS:
            btn = NavButton(icon, tr(i18n_key))
            btn.clicked.connect(lambda _, k=key: self._navigate_to(k))
            self._nav_buttons[key] = btn
            bottom_layout.addWidget(btn)

        layout.addWidget(bottom_widget)

        # ── 언어 선택 콤보 ───────────────────────────────────────
        lang_widget = QWidget()
        lang_widget.setStyleSheet(
            f"background: {C_SIDEBAR_BG}; border-top: 1px solid {C_DIVIDER};"
        )
        lang_layout = QHBoxLayout(lang_widget)
        lang_layout.setContentsMargins(12, 8, 12, 12)

        from PyQt6.QtWidgets import QComboBox
        self._lang_combo = QComboBox()
        self._lang_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C_ITEM_DEFAULT};
                border: 1px solid {C_DIVIDER};
                border-radius: 6px;
                padding: 5px 10px;
                color: #555;
                font-size: 12px;
            }}
            QComboBox:hover {{ background: {C_ITEM_HOVER}; }}
        """)
        for code, display in get_supported_languages():
            self._lang_combo.addItem(f"🌐 {display}", code)
        # 현재 언어 설정
        current = get_language()
        for i in range(self._lang_combo.count()):
            if self._lang_combo.itemData(i) == current:
                self._lang_combo.setCurrentIndex(i)
                break
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self._lang_combo)
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
            "visa": VisaAreaView,
            "health": HealthAreaView,
            "family": FamilyAreaView,
            "education": EducationAreaView,
            "job": JobAreaView,
            "news": NewsView,
            "law": LawView,
            "support": SupportView,
            "search": SearchView,
            "bookmark": BookmarkView,
            "settings": SettingsView,
            "help": HelpView,
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

            # 설정 뷰 시그널 연결
            if key == "settings" and hasattr(view, "refresh_requested"):
                view.refresh_requested.connect(self._manual_refresh)
                view.export_requested.connect(self._export_data)

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

    def _on_language_changed(self, index: int) -> None:
        """언어 콤보박스 변경 시 UI 언어를 전환한다."""
        code = self._lang_combo.itemData(index)
        if code and code != get_language():
            set_language(code)
            self._update_ui_language()

    def _update_ui_language(self) -> None:
        """현재 언어로 사이드바 텍스트를 갱신한다."""
        self._app_name_label.setText(tr("app_name"))

        # 섹션 라벨 갱신
        for i18n_key, label_widget in self._section_labels:
            label_widget.setText(tr(i18n_key).upper())

        # 네비 버튼 텍스트 갱신 — key로 i18n_key 매핑
        _key_to_i18n = {}
        for group in _MENU_GROUPS:
            for icon, i18n_key, nav_key in group["items"]:
                _key_to_i18n[nav_key] = (icon, i18n_key)
        for icon, i18n_key, nav_key in _BOTTOM_ITEMS:
            _key_to_i18n[nav_key] = (icon, i18n_key)

        for nav_key, btn in self._nav_buttons.items():
            if nav_key in _key_to_i18n:
                icon, i18n_key = _key_to_i18n[nav_key]
                btn.setText(f"  {icon}  {tr(i18n_key)}")

    def update_status(self, message: str) -> None:
        self._status_bar.showMessage(message)

    def closeEvent(self, event) -> None:
        """종료 시 트레이 아이콘 정리."""
        if hasattr(self, "_tray_icon"):
            self._tray_icon.hide()
        super().closeEvent(event)
