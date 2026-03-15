"""지원사업 뷰 — 필터 + 목록(좌) + 상세(우)"""
from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QScrollArea, QLabel,
)
from PyQt6.QtCore import Qt

from app.services.data_provider import DataProvider
from app.ui.widgets.search_bar import SearchBar
from app.ui.widgets.filter_bar import FilterBar
from app.ui.widgets.item_card import SupportCard
from app.ui.widgets.detail_panel import DetailPanel


class SupportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = DataProvider.get_all_support()
        self._build_ui()
        self._populate_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 상단 바
        top_bar = QWidget()
        top_bar.setStyleSheet("background: white; border-bottom: 1px solid #E0E0E0;")
        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 12, 16, 12)
        top_layout.setSpacing(8)

        header = QLabel("🏛️ 지원사업")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(header)

        self._search = SearchBar("지원사업 검색...")
        self._search.searched.connect(self._on_search)
        top_layout.addWidget(self._search)

        self._filter = FilterBar([
            ("기관유형", ["전체", "중앙", "지자체", "민간"]),
            ("지역", ["전체", "전국", "서울", "경기", "부산", "대구", "인천"]),
        ])
        self._filter.changed.connect(self._on_filter)
        top_layout.addWidget(self._filter)
        layout.addWidget(top_bar)

        # 분할 패널
        splitter = QSplitter(Qt.Orientation.Horizontal)

        list_area = QScrollArea()
        list_area.setWidgetResizable(True)
        list_area.setStyleSheet("QScrollArea { border: none; background: #FAFAFA; }")
        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        list_area.setWidget(self._list_container)
        splitter.addWidget(list_area)

        self._detail = DetailPanel()
        self._detail.link_clicked.connect(lambda url: webbrowser.open(url))
        splitter.addWidget(self._detail)
        splitter.setSizes([450, 550])
        layout.addWidget(splitter)

    def _populate_list(self, items: list[dict] | None = None) -> None:
        while self._list_layout.count():
            child = self._list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        data = items if items is not None else self._data
        if not data:
            empty = QLabel("검색 결과가 없습니다.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #9E9E9E; padding: 40px;")
            self._list_layout.addWidget(empty)
        else:
            for item in data:
                card = SupportCard(item)
                card.clicked.connect(self._show_detail)
                card.bookmark_toggled.connect(self._on_bookmark)
                self._list_layout.addWidget(card)

        self._list_layout.addStretch()

    def _on_bookmark(self, item_id: int, _new_state: bool) -> None:
        DataProvider.toggle_bookmark("support", item_id)

    def _show_detail(self, item_id: int) -> None:
        item = next((s for s in self._data if s["id"] == item_id), None)
        if not item:
            return
        self._detail.show_detail(
            title=item["name"],
            meta_lines=[
                f"🏢 {item['organizer']} ({item['org_type']})",
                f"📍 {item['region']}",
                f"👥 대상: {item['target_group']}",
                f"📅 {item['apply_start']} ~ {item['apply_end']}",
                f"📞 {item['contact']}",
                f"",
                f"💰 지원 내용: {item['benefit']}",
            ],
            body=item["description"],
            url=item.get("url", ""),
        )

    def refresh_data(self) -> None:
        self._data = DataProvider.get_all_support()
        self._populate_list()

    def _on_search(self, text: str) -> None:
        t = text.lower()
        filtered = [s for s in self._data if t in s["name"].lower() or t in s.get("description", "").lower()]
        self._populate_list(filtered)

    def _on_filter(self) -> None:
        vals = self._filter.get_values()
        filtered = list(self._data)
        org = vals.get("기관유형", "전체")
        if org != "전체":
            filtered = [s for s in filtered if s.get("org_type") == org]
        region = vals.get("지역", "전체")
        if region != "전체":
            filtered = [s for s in filtered if s.get("region") == region]
        self._populate_list(filtered)
