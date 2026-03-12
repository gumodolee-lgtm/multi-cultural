"""설정 뷰 — 언어, 알림, 업데이트 주기, 데이터 관리"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QHBoxLayout, QComboBox, QCheckBox, QSpinBox, QPushButton,
    QGroupBox, QFormLayout,
)
from PyQt6.QtCore import Qt

from app.ui.styles import COLORS


class SettingsView(QWidget):
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
        header = QLabel("⚙️ 설정")
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
        group = self._make_group("🌐 일반")
        form = QFormLayout(group)
        form.setSpacing(12)

        # 언어
        lang = QComboBox()
        lang.addItems(["한국어", "English", "Tiếng Việt", "中文"])
        lang.setMinimumWidth(200)
        form.addRow("인터페이스 언어:", lang)

        # 테마
        theme = QComboBox()
        theme.addItems(["라이트", "다크", "시스템 설정 따르기"])
        theme.setMinimumWidth(200)
        form.addRow("테마:", theme)

        # 글자 크기
        font_size = QComboBox()
        font_size.addItems(["작게 (11pt)", "보통 (13pt)", "크게 (16pt)"])
        font_size.setCurrentIndex(1)
        font_size.setMinimumWidth(200)
        form.addRow("글자 크기:", font_size)

        # 기본 지역
        region = QComboBox()
        region.addItems(["전국", "서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종",
                        "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])
        region.setMinimumWidth(200)
        form.addRow("기본 지역:", region)

        return group

    def _build_notification_group(self) -> QGroupBox:
        group = self._make_group("🔔 알림")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        checks = [
            ("법령 개정 알림", True),
            ("새 뉴스 알림", True),
            ("지원사업 마감 임박 알림 (D-7, D-1)", True),
            ("관심 키워드 매칭 알림", False),
        ]
        for text, checked in checks:
            cb = QCheckBox(text)
            cb.setChecked(checked)
            layout.addWidget(cb)

        # 알림 키워드 관리
        kw_label = QLabel("📝 관심 키워드: 다문화, 결혼이민, 귀화, 외국인 주민")
        kw_label.setStyleSheet("color: #757575; font-size: 12px; padding-top: 8px;")
        layout.addWidget(kw_label)

        edit_btn = QPushButton("키워드 관리")
        edit_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #1565C0; border: 1px solid #1565C0;"
            " border-radius: 4px; padding: 4px 12px; }"
            "QPushButton:hover { background: #E3F2FD; }"
        )
        edit_btn.setFixedWidth(120)
        layout.addWidget(edit_btn)

        return group

    def _build_scheduler_group(self) -> QGroupBox:
        group = self._make_group("🔄 자동 업데이트")
        form = QFormLayout(group)
        form.setSpacing(12)

        news_spin = QSpinBox()
        news_spin.setRange(15, 360)
        news_spin.setValue(60)
        news_spin.setSuffix(" 분")
        form.addRow("뉴스 수집 주기:", news_spin)

        law_spin = QSpinBox()
        law_spin.setRange(1, 72)
        law_spin.setValue(24)
        law_spin.setSuffix(" 시간")
        form.addRow("법령 확인 주기:", law_spin)

        support_spin = QSpinBox()
        support_spin.setRange(1, 72)
        support_spin.setValue(12)
        support_spin.setSuffix(" 시간")
        form.addRow("지원사업 확인 주기:", support_spin)

        return group

    def _build_data_group(self) -> QGroupBox:
        group = self._make_group("💾 데이터 관리")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        info = QLabel("데이터베이스: data/michub.db")
        info.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(info)

        row = QHBoxLayout()

        refresh_btn = QPushButton("🔄 지금 업데이트")
        refresh_btn.setStyleSheet(
            "QPushButton { background: #1565C0; color: white; border: none;"
            " border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #0D47A1; }"
        )
        row.addWidget(refresh_btn)

        export_btn = QPushButton("📥 데이터 내보내기")
        export_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #1565C0; border: 1px solid #1565C0;"
            " border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #E3F2FD; }"
        )
        row.addWidget(export_btn)

        clear_btn = QPushButton("🗑️ 전체 초기화")
        clear_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #D32F2F; border: 1px solid #D32F2F;"
            " border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #FFEBEE; }"
        )
        row.addWidget(clear_btn)

        row.addStretch()
        layout.addLayout(row)

        return group

    def _build_about_group(self) -> QGroupBox:
        group = self._make_group("ℹ️ 정보")
        layout = QVBoxLayout(group)

        about_text = (
            "다문화 정보 허브 v0.1.0\n"
            "다문화 관련 뉴스·법령·지원사업을 한 곳에서 확인하세요.\n\n"
            "기술 스택: Python 3.12 + PyQt6\n"
            "데이터베이스: SQLite + SQLAlchemy\n"
            "라이선스: MIT"
        )
        about = QLabel(about_text)
        about.setStyleSheet("color: #616161; font-size: 12px;")
        about.setWordWrap(True)
        layout.addWidget(about)

        return group
