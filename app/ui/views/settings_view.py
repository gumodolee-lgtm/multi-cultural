"""설정 뷰 — 언어, 알림, 업데이트 주기, 데이터 관리 (영구 저장)"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QHBoxLayout, QComboBox, QCheckBox, QSpinBox, QPushButton,
    QGroupBox, QFormLayout, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.services.settings_service import get_setting, set_setting
from app.ui.styles import COLORS
from app.utils.i18n import tr

# 언어 코드 ↔ 콤보박스 인덱스 매핑
_LANG_CODES = ["ko", "en", "vi", "zh"]
_LANG_LABELS = ["한국어", "English", "Tiếng Việt", "中文"]

# 테마 코드 ↔ 인덱스
_THEME_CODES = ["light", "dark"]

# 글자 크기 옵션
_FONT_SIZES = ["11pt", "13pt", "16pt"]

# 지역 옵션
_REGIONS = [
    "전국", "서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종",
    "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
]


class SettingsView(QWidget):
    # 외부(MainWindow)에서 연결할 시그널
    refresh_requested = pyqtSignal()
    export_requested = pyqtSignal()
    language_changed = pyqtSignal(str)   # 언어 변경 시 코드 전달
    theme_changed = pyqtSignal(str)      # 테마 변경 시 코드 전달

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F5F5F5; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # 헤더
        header = QLabel(tr("settings_title"))
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #212121;")
        layout.addWidget(header)

        # 1. 일반 설정
        layout.addWidget(self._build_general_group())

        # 2. 알림 설정
        layout.addWidget(self._build_notification_group())

        # 3. 업데이트 주기
        layout.addWidget(self._build_scheduler_group())

        # 4. 데이터 관리
        layout.addWidget(self._build_data_group())

        # 5. 정보
        layout.addWidget(self._build_about_group())

        layout.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_group(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
                margin-top: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #1565C0;
            }
        """)
        return group

    # ------------------------------------------------------------------
    # 1. 일반 설정
    # ------------------------------------------------------------------
    def _build_general_group(self) -> QGroupBox:
        group = self._make_group(tr("general"))
        form = QFormLayout(group)
        form.setSpacing(12)

        # 언어
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(_LANG_LABELS)
        saved_lang = get_setting("language")
        if saved_lang in _LANG_CODES:
            self._lang_combo.setCurrentIndex(_LANG_CODES.index(saved_lang))
        self._lang_combo.setMinimumWidth(200)
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        form.addRow(tr("interface_lang"), self._lang_combo)

        # 테마
        self._theme_combo = QComboBox()
        self._theme_combo.addItems([tr("theme_light"), tr("theme_dark")])
        saved_theme = get_setting("theme")
        if saved_theme in _THEME_CODES:
            self._theme_combo.setCurrentIndex(_THEME_CODES.index(saved_theme))
        self._theme_combo.setMinimumWidth(200)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        form.addRow(tr("theme"), self._theme_combo)

        # 글자 크기
        self._font_combo = QComboBox()
        self._font_combo.addItems(_FONT_SIZES)
        saved_font = get_setting("font_size")
        if saved_font in _FONT_SIZES:
            self._font_combo.setCurrentIndex(_FONT_SIZES.index(saved_font))
        self._font_combo.setMinimumWidth(200)
        self._font_combo.currentIndexChanged.connect(self._on_font_changed)
        form.addRow(tr("font_size"), self._font_combo)

        # 기본 지역
        self._region_combo = QComboBox()
        self._region_combo.addItems(_REGIONS)
        saved_region = get_setting("default_region")
        if saved_region in _REGIONS:
            self._region_combo.setCurrentIndex(_REGIONS.index(saved_region))
        self._region_combo.setMinimumWidth(200)
        self._region_combo.currentIndexChanged.connect(self._on_region_changed)
        form.addRow(tr("default_region"), self._region_combo)

        return group

    # ------------------------------------------------------------------
    # 2. 알림 설정
    # ------------------------------------------------------------------
    def _build_notification_group(self) -> QGroupBox:
        group = self._make_group(tr("notifications"))
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self._notify_checks = {}
        notify_keys = [
            ("notify_law", tr("notify_law")),
            ("notify_news", tr("notify_news")),
            ("notify_support_deadline", tr("notify_support_deadline")),
            ("notify_keyword", tr("notify_keyword")),
        ]
        for key, text in notify_keys:
            cb = QCheckBox(text)
            cb.setChecked(get_setting(key) == "true")
            cb.stateChanged.connect(lambda state, k=key: self._on_notify_changed(k, state))
            self._notify_checks[key] = cb
            layout.addWidget(cb)

        edit_btn = QPushButton(tr("manage_keywords"))
        edit_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #1565C0; border: 1px solid #1565C0;"
            " border-radius: 4px; padding: 4px 12px; }"
            "QPushButton:hover { background: #E3F2FD; }"
        )
        edit_btn.setFixedWidth(140)
        edit_btn.clicked.connect(self._on_manage_keywords)
        layout.addWidget(edit_btn)

        return group

    # ------------------------------------------------------------------
    # 3. 업데이트 주기
    # ------------------------------------------------------------------
    def _build_scheduler_group(self) -> QGroupBox:
        group = self._make_group(tr("auto_update"))
        form = QFormLayout(group)
        form.setSpacing(12)

        self._news_spin = QSpinBox()
        self._news_spin.setRange(15, 360)
        self._news_spin.setValue(int(get_setting("news_interval_min")))
        self._news_spin.setSuffix(tr("minutes"))
        self._news_spin.valueChanged.connect(
            lambda v: set_setting("news_interval_min", str(v))
        )
        form.addRow(tr("news_interval"), self._news_spin)

        self._law_spin = QSpinBox()
        self._law_spin.setRange(1, 72)
        self._law_spin.setValue(int(get_setting("law_interval_hr")))
        self._law_spin.setSuffix(tr("hours"))
        self._law_spin.valueChanged.connect(
            lambda v: set_setting("law_interval_hr", str(v))
        )
        form.addRow(tr("law_interval"), self._law_spin)

        self._support_spin = QSpinBox()
        self._support_spin.setRange(1, 72)
        self._support_spin.setValue(int(get_setting("support_interval_hr")))
        self._support_spin.setSuffix(tr("hours"))
        self._support_spin.valueChanged.connect(
            lambda v: set_setting("support_interval_hr", str(v))
        )
        form.addRow(tr("support_interval"), self._support_spin)

        return group

    # ------------------------------------------------------------------
    # 4. 데이터 관리
    # ------------------------------------------------------------------
    def _build_data_group(self) -> QGroupBox:
        group = self._make_group(tr("data_management"))
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self._db_info = QLabel("DB: data/michub.db")
        self._db_info.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(self._db_info)

        row = QHBoxLayout()

        refresh_btn = QPushButton(tr("update_now"))
        refresh_btn.setStyleSheet(
            "QPushButton { background: #1565C0; color: white; border: none;"
            " border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #0D47A1; }"
        )
        refresh_btn.clicked.connect(self._on_refresh)
        row.addWidget(refresh_btn)

        export_btn = QPushButton(tr("export_data"))
        export_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #1565C0; border: 1px solid #1565C0;"
            " border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #E3F2FD; }"
        )
        export_btn.clicked.connect(self._on_export)
        row.addWidget(export_btn)

        clear_btn = QPushButton(tr("reset_all"))
        clear_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #D32F2F; border: 1px solid #D32F2F;"
            " border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #FFEBEE; }"
        )
        clear_btn.clicked.connect(self._on_clear)
        row.addWidget(clear_btn)

        row.addStretch()
        layout.addLayout(row)

        return group

    # ------------------------------------------------------------------
    # 5. 정보
    # ------------------------------------------------------------------
    def _build_about_group(self) -> QGroupBox:
        group = self._make_group(tr("about"))
        layout = QVBoxLayout(group)

        about_text = (
            f"{tr('app_name')} v0.1.0\n\n"
            "Python 3.12 + PyQt6\n"
            "SQLite + SQLAlchemy\n"
            "MIT License"
        )
        about = QLabel(about_text)
        about.setStyleSheet("color: #616161; font-size: 12px;")
        about.setWordWrap(True)
        layout.addWidget(about)

        return group

    # ------------------------------------------------------------------
    # 핸들러
    # ------------------------------------------------------------------
    def _on_lang_changed(self, index: int) -> None:
        code = _LANG_CODES[index]
        set_setting("language", code)
        self.language_changed.emit(code)

    def _on_theme_changed(self, index: int) -> None:
        code = _THEME_CODES[index]
        set_setting("theme", code)
        self.theme_changed.emit(code)

    def _on_font_changed(self, index: int) -> None:
        set_setting("font_size", _FONT_SIZES[index])

    def _on_region_changed(self, index: int) -> None:
        set_setting("default_region", _REGIONS[index])

    def _on_notify_changed(self, key: str, state: int) -> None:
        set_setting(key, "true" if state else "false")

    def _on_manage_keywords(self) -> None:
        from app.ui.widgets.keyword_dialog import KeywordDialog
        dlg = KeywordDialog(parent=self)
        dlg.exec()

    def _on_refresh(self) -> None:
        self._db_info.setText(tr("updating"))
        self.refresh_requested.emit()

    def _on_export(self) -> None:
        self.export_requested.emit()

    def _on_clear(self) -> None:
        reply = QMessageBox.question(
            self, tr("reset_confirm_title"),
            tr("reset_confirm_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._clear_database()

    def _clear_database(self) -> None:
        """DB의 모든 데이터를 삭제한다."""
        from app.models.database import get_session
        from app.models.news import News
        from app.models.law import Law
        from app.models.support import SupportProgram

        session_gen = get_session()
        session = next(session_gen)
        try:
            session.query(News).delete()
            session.query(Law).delete()
            session.query(SupportProgram).delete()
            session.commit()
            self._db_info.setText(tr("data_reset_done"))
        except Exception as e:
            session.rollback()
            self._db_info.setText(f"Error: {e}")
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass
