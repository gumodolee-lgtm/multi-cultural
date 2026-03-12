"""대시보드 뷰 — KPI 카드 + 오늘의 뉴스 + 마감 임박"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt

from app.ui.mock_data import MOCK_DASHBOARD, MOCK_NEWS, MOCK_SUPPORT
from app.ui.styles import COLORS


class DashboardView(QWidget):
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

        # 환영 메시지
        welcome = QLabel("📋 대시보드")
        welcome.setStyleSheet("font-size: 22px; font-weight: bold; color: #212121;")
        layout.addWidget(welcome)

        sub = QLabel(f"마지막 업데이트: {MOCK_DASHBOARD['last_update']}")
        sub.setStyleSheet("color: #9E9E9E; font-size: 12px;")
        layout.addWidget(sub)

        # KPI 카드 행
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_data = [
            ("📰", "수집 뉴스", str(MOCK_DASHBOARD["news_count"]), COLORS["primary"]),
            ("⚖️", "주요 법령", str(MOCK_DASHBOARD["law_count"]), "#2E7D32"),
            ("🏛️", "지원사업", str(MOCK_DASHBOARD["support_count"]), COLORS["accent"]),
            ("🔔", "오늘 뉴스", str(MOCK_DASHBOARD["today_news"]), COLORS["danger"]),
            ("⏰", "마감 임박", str(MOCK_DASHBOARD["closing_soon"]), "#7B1FA2"),
            ("⭐", "북마크", str(MOCK_DASHBOARD["bookmarked"]), COLORS["bookmark"]),
        ]
        for icon, label, value, color in kpi_data:
            card = self._make_kpi_card(icon, label, value, color)
            kpi_row.addWidget(card)
        layout.addLayout(kpi_row)

        # 오늘의 주요 뉴스
        layout.addWidget(self._section_title("📰 최근 뉴스"))
        for news in MOCK_NEWS[:3]:
            layout.addWidget(self._news_item(news))

        # 마감 임박 지원사업
        layout.addWidget(self._section_title("⏰ 마감 임박 지원사업"))
        closing = [s for s in MOCK_SUPPORT if s["apply_end"] >= "2026-03-01"]
        for sp in closing[:3]:
            layout.addWidget(self._support_item(sp))

        layout.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_kpi_card(self, icon: str, label: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(
            f"QFrame {{ background: white; border: 1px solid #E0E0E0;"
            f" border-radius: 12px; border-left: 4px solid {color}; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)

        top = QLabel(f"{icon}  {label}")
        top.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(top)

        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        layout.addWidget(val)

        return card

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #212121;"
            " padding-top: 8px; border-bottom: 2px solid #1565C0; padding-bottom: 4px;"
        )
        return lbl

    def _news_item(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #1565C0; }"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        left = QVBoxLayout()
        title = QLabel(data["title"])
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        left.addWidget(title)

        meta = QLabel(f"{data['source']}  ·  {data['published']}  ·  {data['category']}")
        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        left.addWidget(meta)
        layout.addLayout(left, 1)

        return frame

    def _support_item(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #FF8F00; }"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        left = QVBoxLayout()
        title = QLabel(data["name"])
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        left.addWidget(title)

        meta = QLabel(f"{data['organizer']}  ·  마감: {data['apply_end']}  ·  {data['region']}")
        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        left.addWidget(meta)
        layout.addLayout(left, 1)

        deadline = QLabel(f"D-?")
        deadline.setStyleSheet(
            "color: #D32F2F; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(deadline)

        return frame
