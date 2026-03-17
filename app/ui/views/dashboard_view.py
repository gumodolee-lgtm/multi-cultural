"""대시보드 뷰 — KPI 카드 + 오늘의 뉴스 + 마감 임박"""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt

from app.services.data_provider import DataProvider
from app.ui import styles
from app.ui.widgets.detail_dialog import DetailDialog
from app.utils.i18n import tr


class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll = None
        self._build_ui()

    def _build_ui(self) -> None:
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {styles.COLORS.background}; }}")

        self._rebuild_content()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

    def refresh_data(self) -> None:
        """데이터를 DB에서 다시 읽어 대시보드를 갱신한다."""
        # 기존 스크롤 내부 컨텐츠만 교체 (레이아웃은 유지)
        if self._scroll is not None:
            old_widget = self._scroll.widget()
            if old_widget:
                old_widget.deleteLater()
            self._rebuild_content()

    def _rebuild_content(self) -> None:
        """스크롤 영역 안의 컨텐츠를 새로 구성한다."""
        stats = DataProvider.get_dashboard_stats()
        all_news = DataProvider.get_all_news()
        all_support = DataProvider.get_all_support()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # 환영 메시지
        welcome = QLabel(tr("dashboard_title"))
        welcome.setStyleSheet(f"{styles.FONTS.h1} color: {styles.COLORS.text_primary};")
        layout.addWidget(welcome)

        sub = QLabel(f"{tr('last_update')}: {stats['last_update']}")
        sub.setStyleSheet(f"{styles.FONTS.caption} color: {styles.COLORS.text_secondary};")
        layout.addWidget(sub)

        # KPI 카드 행
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_data = [
            ("📰", tr("collected_news"), str(stats["news_count"]), styles.COLORS.primary),
            ("⚖️", tr("major_laws"), str(stats["law_count"]), "#2E7D32"), # 초록색 유지
            ("🏛️", tr("support_programs"), str(stats["support_count"]), styles.COLORS.accent),
            ("🔔", tr("today_news"), str(stats["today_news"]), styles.COLORS.danger),
            ("⏰", tr("closing_soon"), str(stats["closing_soon"]), "#7B1FA2"), # 보라색 유지
            ("⭐", tr("bookmarked"), str(stats["bookmarked"]), styles.COLORS.bookmark),
        ]
        for icon, label, value, color in kpi_data:
            card = self._make_kpi_card(icon, label, value, color)
            kpi_row.addWidget(card)
        layout.addLayout(kpi_row)

        # 오늘의 주요 뉴스
        layout.addWidget(self._section_title(tr("recent_news")))
        for news in all_news[:3]:
            layout.addWidget(self._news_item(news))

        # 마감 임박 지원사업
        layout.addWidget(self._section_title(tr("closing_support")))
        today_str = datetime.now().strftime("%Y-%m-%d")
        closing = [s for s in all_support if s.get("apply_end", "") >= today_str]
        closing.sort(key=lambda s: s.get("apply_end", "9999"))
        for sp in closing[:3]:
            layout.addWidget(self._support_item(sp))

        # 다문화가족실태조사 통계
        survey_data = DataProvider.get_survey_stats()
        if survey_data:
            layout.addWidget(self._section_title(tr("survey_stats_title")))
            layout.addWidget(self._survey_section(survey_data))

        layout.addStretch()
        self._scroll.setWidget(container)

    def _make_kpi_card(self, icon: str, label: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(styles.get_kpi_card_style(color))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        top = QLabel(f"{icon}  {label}")
        top.setStyleSheet(f"{styles.FONTS.caption} color: {styles.COLORS.text_secondary};")
        layout.addWidget(top)

        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        layout.addWidget(val)

        return card

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(styles.get_section_title_style(styles.COLORS.primary))
        return lbl

    def _news_item(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setStyleSheet(styles.get_card_style(hover_color=styles.COLORS.primary))
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        left = QVBoxLayout()
        title = QLabel(data["title"])
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setStyleSheet(f"{styles.FONTS.body} font-weight: bold; color: {styles.COLORS.text_primary};")
        title.setWordWrap(True)
        left.addWidget(title)

        meta = QLabel(f"{data.get('source', '')}  ·  {data.get('published', '')}  ·  {data.get('category', '')}")
        meta.setTextFormat(Qt.TextFormat.PlainText)
        meta.setStyleSheet(f"{styles.FONTS.small} color: {styles.COLORS.text_secondary};")
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
        frame.setStyleSheet(styles.get_card_style(hover_color=styles.COLORS.secondary))
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        left = QVBoxLayout()
        title = QLabel(data.get("name", ""))
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setStyleSheet(f"{styles.FONTS.body} font-weight: bold; color: {styles.COLORS.text_primary};")
        title.setWordWrap(True)
        left.addWidget(title)

        meta = QLabel(f"{data.get('organizer', '')}  ·  마감: {data.get('apply_end', '')}  ·  {data.get('region', '')}")
        meta.setTextFormat(Qt.TextFormat.PlainText)
        meta.setStyleSheet(f"{styles.FONTS.small} color: {styles.COLORS.text_secondary};")
        left.addWidget(meta)
        layout.addLayout(left, 1)

        # D-day 계산
        d_day = "D-?"
        try:
            end = datetime.strptime(data.get("apply_end", ""), "%Y-%m-%d")
            diff = (end - datetime.now()).days
            d_day = f"D-{diff}" if diff >= 0 else tr("deadline")
        except ValueError:
            pass

        deadline = QLabel(d_day)
        deadline.setStyleSheet(f"color: {styles.COLORS.danger}; {styles.FONTS.h3}")
        layout.addWidget(deadline)

        frame.mousePressEvent = lambda e, d=data: self._open_support_detail(d)
        return frame

    def _survey_section(self, data: list[dict]) -> QFrame:
        """다문화가족실태조사 통계 표시 카드"""
        frame = QFrame()
        frame.setStyleSheet(styles.get_card_style())
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # 조사 연도 목록을 가로 카드로 표시
        row = QHBoxLayout()
        row.setSpacing(12)
        for item in data:
            year_card = QFrame()
            year_card.setStyleSheet(
                f"QFrame {{ background: {styles.COLORS.primary}; border: 1px solid {styles.COLORS.primary_dark};"
                " border-radius: 8px; }"
            )
            year_layout = QVBoxLayout(year_card)
            year_layout.setContentsMargins(16, 10, 16, 10)

            year_label = QLabel(item["survey_year"])
            year_label.setStyleSheet(f"{styles.FONTS.h1} color: {styles.COLORS.text_on_primary};")
            year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            year_layout.addWidget(year_label)

            name_label = QLabel(tr("survey_year"))
            name_label.setStyleSheet(f"{styles.FONTS.small} color: #BBDEFB;") # 밝은 파랑
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            year_layout.addWidget(name_label)

            row.addWidget(year_card)
        row.addStretch()
        layout.addLayout(row)

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
