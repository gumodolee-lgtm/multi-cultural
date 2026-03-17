"""뉴스 뷰 — 목록 패널(좌) + 상세 패널(우) 분할"""
from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QScrollArea, QLabel,
)
from PyQt6.QtCore import Qt

from app.services.data_provider import DataProvider
from app.ui import styles
from app.ui.widgets.search_bar import SearchBar
from app.ui.widgets.filter_bar import FilterBar
from app.ui.widgets.item_card import NewsCard
from app.ui.widgets.detail_panel import DetailPanel
from app.utils.i18n import tr


class NewsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = DataProvider.get_all_news()
        self._build_ui()
        self._populate_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 상단 바 (검색 + 필터)
        top_bar = QWidget()
        top_bar.setStyleSheet(f"background: {styles.COLORS.surface}; border-bottom: 1px solid {styles.COLORS.divider};")
        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 12, 16, 12)
        top_layout.setSpacing(8)

        header = QLabel(f"📰 {tr('news')}")
        header.setStyleSheet(f"{styles.FONTS.h2} color: {styles.COLORS.text_primary};")
        top_layout.addWidget(header)

        self._search = SearchBar(tr("news_search"))
        self._search.searched.connect(self._on_search)
        top_layout.addWidget(self._search)

        self._filter = FilterBar([
            ("카테고리", ["전체", "정책", "지역", "국제", "사례"]),
            ("출처", ["전체", "연합뉴스", "KBS", "뉴시스", "한겨레", "서울신문"]),
        ])
        self._filter.changed.connect(self._on_filter)
        top_layout.addWidget(self._filter)
        layout.addWidget(top_bar)

        # 분할 패널
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 좌측: 뉴스 목록
        list_area = QScrollArea()
        list_area.setWidgetResizable(True)
        list_area.setStyleSheet(f"QScrollArea {{ border: none; background: {styles.COLORS.background}; }}")
        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        list_area.setWidget(self._list_container)
        splitter.addWidget(list_area)

        # 우측: 상세 패널
        self._detail = DetailPanel()
        self._detail.link_clicked.connect(lambda url: webbrowser.open(url))
        splitter.addWidget(self._detail)

        splitter.setSizes([450, 550])
        layout.addWidget(splitter)

    def _populate_list(self, items: list[dict] | None = None) -> None:
        # 기존 위젯 제거
        while self._list_layout.count():
            child = self._list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        data = items if items is not None else self._data
        if not data:
            empty = QLabel(tr("no_results"))
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"color: {styles.COLORS.text_secondary}; padding: 40px;")
            self._list_layout.addWidget(empty)
        else:
            for item in data:
                card = NewsCard(item)
                card.clicked.connect(self._show_detail)
                card.bookmark_toggled.connect(self._on_bookmark)
                self._list_layout.addWidget(card)

        self._list_layout.addStretch()

    def _show_detail(self, item_id: int) -> None:
        item = next((n for n in self._data if n["id"] == item_id), None)
        if not item:
            return
        # AI 요약 (로컬 폴백)
        summary = item.get("summary", "")
        if not summary and item.get("content"):
            from app.services.ai_summary import AISummaryService
            from app.utils.config_loader import load_config
            svc = AISummaryService(load_config())
            summary = svc.summarize_news(item["title"], item["content"])
        meta = [
            f"<b>{tr('source')}:</b> {item['source']}  ·  <b>{tr('category')}:</b> {item['category']}",
            f"<b>{tr('published_date')}:</b> {item['published']}",
        ]
        if summary:
            meta.append("")
            meta.append(f"💡 <b>{tr('ai_summary')}:</b> {summary}")
        self._detail.show_detail(
            title=item["title"],
            meta_lines=meta,
            body=item["content"],
            url=item.get("url", ""),
        )

    def refresh_data(self) -> None:
        """데이터를 DB에서 다시 읽어 목록을 갱신한다."""
        self._data = DataProvider.get_all_news()
        self._populate_list()

    def _on_search(self, text: str) -> None:
        if text.strip():
            filtered = DataProvider.search_news(keyword=text)
            self._populate_list(filtered)
        else:
            self._data = DataProvider.get_all_news()
            self._populate_list()

    def _on_bookmark(self, item_id: int, _new_state: bool) -> None:
        DataProvider.toggle_bookmark("news", item_id)

    def _on_filter(self) -> None:
        vals = self._filter.get_values()
        cat = vals.get("카테고리", "전체")
        src = vals.get("출처", "전체")
        filtered = DataProvider.search_news(category=cat, source=src)
        self._populate_list(filtered)
