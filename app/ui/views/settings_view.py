"""설정 뷰 — 언어, 알림, 업데이트 주기, 데이터 관리"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QHBoxLayout, QComboBox, QCheckBox, QSpinBox, QPushButton,
    QGroupBox, QFormLayout, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.ui.styles import COLORS
from app.utils.i18n import tr


class SettingsView(QWidget):
    # 외부(MainWindow)에서 연결할 시그널
    refresh_requested = pyqtSignal()
    export_requested = pyqtSignal()

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

    def _build_general_group(self) -> QGroupBox:
        group = self._make_group(tr("general"))
        form = QFormLayout(group)
        form.setSpacing(12)

        # 언어
        lang = QComboBox()
        lang.addItems(["한국어", "English", "Tiếng Việt", "中文"])
        lang.setMinimumWidth(200)
        form.addRow(tr("interface_lang"), lang)

        # 테마
        theme = QComboBox()
        theme.addItems([tr("theme_light"), tr("theme_dark"), tr("theme_system")])
        theme.setMinimumWidth(200)
        form.addRow(tr("theme"), theme)

        # 글자 크기
        font_size = QComboBox()
        font_size.addItems(["11pt", "13pt", "16pt"])
        font_size.setCurrentIndex(1)
        font_size.setMinimumWidth(200)
        form.addRow(tr("font_size"), font_size)

        # 기본 지역
        region = QComboBox()
        region.addItems(["전국", "서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종",
                        "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])
        region.setMinimumWidth(200)
        form.addRow(tr("default_region"), region)

        return group

    def _build_notification_group(self) -> QGroupBox:
        group = self._make_group(tr("notifications"))
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        checks = [
            (tr("notify_law"), True),
            (tr("notify_news"), True),
            (tr("notify_support_deadline"), True),
            (tr("notify_keyword"), False),
        ]
        for text, checked in checks:
            cb = QCheckBox(text)
            cb.setChecked(checked)
            layout.addWidget(cb)

        edit_btn = QPushButton(tr("manage_keywords"))
        edit_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #1565C0; border: 1px solid #1565C0;"
            " border-radius: 4px; padding: 4px 12px; }"
            "QPushButton:hover { background: #E3F2FD; }"
        )
        edit_btn.setFixedWidth(140)
        layout.addWidget(edit_btn)

        return group

    def _build_scheduler_group(self) -> QGroupBox:
        group = self._make_group(tr("auto_update"))
        form = QFormLayout(group)
        form.setSpacing(12)

        news_spin = QSpinBox()
        news_spin.setRange(15, 360)
        news_spin.setValue(60)
        news_spin.setSuffix(tr("minutes"))
        form.addRow(tr("news_interval"), news_spin)

        law_spin = QSpinBox()
        law_spin.setRange(1, 72)
        law_spin.setValue(24)
        law_spin.setSuffix(tr("hours"))
        form.addRow(tr("law_interval"), law_spin)

        support_spin = QSpinBox()
        support_spin.setRange(1, 72)
        support_spin.setValue(12)
        support_spin.setSuffix(tr("hours"))
        form.addRow(tr("support_interval"), support_spin)

        return group

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

    # -- 버튼 핸들러 --

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
