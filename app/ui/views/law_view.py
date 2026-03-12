"""법령 뷰 — 목록 패널(좌) + 상세 패널(우) 분할"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QScrollArea, QLabel,
)
from PyQt6.QtCore import Qt

from app.ui.mock_data import MOCK_LAWS
from app.ui.widgets.search_bar import SearchBar
from app.ui.widgets.filter_bar import FilterBar
from app.ui.widgets.item_card import LawCard
from app.ui.widgets.detail_panel import DetailPanel


class LawView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = list(MOCK_LAWS)
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

        header = QLabel("⚖️ 법령")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(header)

        self._search = SearchBar("법령 검색 (법령명, 조문 키워드)...")
        self._search.searched.connect(self._on_search)
        top_layout.addWidget(self._search)

        self._filter = FilterBar([
            ("분류", ["전체", "다문화", "출입국", "국적"]),
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
                card = LawCard(item)
                card.clicked.connect(self._show_detail)
                self._list_layout.addWidget(card)

        self._list_layout.addStretch()

    def _show_detail(self, item_id: int) -> None:
        item = next((l for l in self._data if l["id"] == item_id), None)
        if not item:
            return
        self._detail.show_detail(
            title=item["name"],
            meta_lines=[
                f"📂 {item['category']}  ·  법령코드: {item['law_code']}",
                f"📅 개정: {item['amended_date']}  ·  시행: {item['effective_date']}",
                f"",
                f"💡 AI 요약: {item['summary']}",
            ],
            body=item["content"],
        )

    def _on_search(self, text: str) -> None:
        t = text.lower()
        filtered = [l for l in self._data if t in l["name"].lower() or t in l.get("content", "").lower()]
        self._populate_list(filtered)

    def _on_filter(self) -> None:
        vals = self._filter.get_values()
        cat = vals.get("분류", "전체")
        if cat == "전체":
            self._populate_list()
        else:
            self._populate_list([l for l in self._data if l.get("category") == cat])
