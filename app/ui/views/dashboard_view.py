"""대시보드 뷰 — KPI 카드 + 오늘의 뉴스 + 마감 임박"""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt

from app.services.data_provider import DataProvider
from app.ui.styles import COLORS
from app.ui.widgets.detail_dialog import DetailDialog


class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll = None
        self._build_ui()

    def _build_ui(self) -> None:
        stats = DataProvider.get_dashboard_stats()
        all_news = DataProvider.get_all_news()
        all_support = DataProvider.get_all_support()

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: #F5F5F5; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # 환영 메시지
        welcome = QLabel("📋 대시보드")
        welcome.setStyleSheet("font-size: 22px; font-weight: bold; color: #212121;")
        layout.addWidget(welcome)

        sub = QLabel(f"마지막 업데이트: {stats['last_update']}")
        sub.setStyleSheet("color: #9E9E9E; font-size: 12px;")
        layout.addWidget(sub)

        # KPI 카드 행
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_data = [
            ("📰", "수집 뉴스", str(stats["news_count"]), COLORS["primary"]),
            ("⚖️", "주요 법령", str(stats["law_count"]), "#2E7D32"),
            ("🏛️", "지원사업", str(stats["support_count"]), COLORS["accent"]),
            ("🔔", "오늘 뉴스", str(stats["today_news"]), COLORS["danger"]),
            ("⏰", "마감 임박", str(stats["closing_soon"]), "#7B1FA2"),
            ("⭐", "북마크", str(stats["bookmarked"]), COLORS["bookmark"]),
        ]
        for icon, label, value, color in kpi_data:
            card = self._make_kpi_card(icon, label, value, color)
            kpi_row.addWidget(card)
        layout.addLayout(kpi_row)

        # 오늘의 주요 뉴스
        layout.addWidget(self._section_title("📰 최근 뉴스"))
        for news in all_news[:3]:
            layout.addWidget(self._news_item(news))

        # 마감 임박 지원사업
        layout.addWidget(self._section_title("⏰ 마감 임박 지원사업"))
        today_str = datetime.now().strftime("%Y-%m-%d")
        closing = [s for s in all_support if s.get("apply_end", "") >= today_str]
        closing.sort(key=lambda s: s.get("apply_end", "9999"))
        for sp in closing[:3]:
            layout.addWidget(self._support_item(sp))

        layout.addStretch()
        self._scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

    def refresh_data(self) -> None:
        """데이터를 DB에서 다시 읽어 대시보드를 갱신한다."""
        # 기존 위젯 제거 후 재구성
        if self.layout():
            while self.layout().count():
                child = self.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            QVBoxLayout(self)
        self._build_ui()

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
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #1565C0; }"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        left = QVBoxLayout()
        title = QLabel(data["title"])
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        left.addWidget(title)

        meta = QLabel(f"{data.get('source', '')}  ·  {data.get('published', '')}  ·  {data.get('category', '')}")
        meta.setTextFormat(Qt.TextFormat.PlainText)
        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        left.addWidget(meta)
        layout.addLayout(left, 1)

        frame.mousePressEvent = lambda e, d=data: self._open_news_detail(d)
        return frame

    def _open_news_detail(self, data: dict) -> None:
        dlg = DetailDialog(
            title=data["title"],
            meta_lines=[
                f"📰 {data.get('source', '')}  ·  {data.get('category', '')}",
                f"📅 {data.get('published', '')}",
            ],
            body=data.get("content", data.get("summary", "")),
            url=data.get("url", ""),
            parent=self,
        )
        dlg.exec()

    def _support_item(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #FF8F00; }"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        left = QVBoxLayout()
        title = QLabel(data.get("name", ""))
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        left.addWidget(title)

        meta = QLabel(f"{data.get('organizer', '')}  ·  마감: {data.get('apply_end', '')}  ·  {data.get('region', '')}")
        meta.setTextFormat(Qt.TextFormat.PlainText)
        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        left.addWidget(meta)
        layout.addLayout(left, 1)

        # D-day 계산
        d_day = "D-?"
        try:
            end = datetime.strptime(data.get("apply_end", ""), "%Y-%m-%d")
            diff = (end - datetime.now()).days
            d_day = f"D-{diff}" if diff >= 0 else "마감"
        except ValueError:
            pass

        deadline = QLabel(d_day)
        deadline.setStyleSheet(
            "color: #D32F2F; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(deadline)

        frame.mousePressEvent = lambda e, d=data: self._open_support_detail(d)
        return frame

    def _open_support_detail(self, data: dict) -> None:
        dlg = DetailDialog(
            title=data.get("name", ""),
            meta_lines=[
                f"🏛️ {data.get('organizer', '')}  ·  {data.get('region', '')}",
                f"📅 {data.get('apply_start', '')} ~ {data.get('apply_end', '')}",
                f"👥 대상: {data.get('target_group', '')}",
            ],
            body=f"💰 지원내용: {data.get('benefit', '')}\n\n📞 연락처: {data.get('contact', '')}",
            url=data.get("url", ""),
            parent=self,
        )
        dlg.exec()
