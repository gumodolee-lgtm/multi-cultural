"""통합 검색 뷰 — 전체 카테고리 검색"""
from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout,
)
from PyQt6.QtCore import Qt

from app.services.data_provider import DataProvider
from app.ui.widgets.search_bar import SearchBar
from app.ui.styles import COLORS
from app.ui.widgets.detail_dialog import DetailDialog


class SearchView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 상단 검색 영역
        top = QWidget()
        top.setStyleSheet("background: #1565C0;")
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(40, 30, 40, 30)
        top_layout.setSpacing(12)

        title = QLabel("🔍 통합 검색")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(title)

        desc = QLabel("뉴스, 법령, 지원사업을 한 번에 검색합니다")
        desc.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 13px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(desc)

        self._search = SearchBar("키워드를 입력하세요...")
        self._search.searched.connect(self._on_search)
        top_layout.addWidget(self._search)
        layout.addWidget(top)

        # 결과 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F5F5F5; }")
        self._result_container = QWidget()
        self._result_layout = QVBoxLayout(self._result_container)
        self._result_layout.setContentsMargins(24, 16, 24, 16)
        self._result_layout.setSpacing(12)
        scroll.setWidget(self._result_container)
        layout.addWidget(scroll)

        # 초기 상태: 인기 검색어 표시
        self._show_initial()

    def _show_initial(self) -> None:
        self._clear_results()

        hint = QLabel("💡 인기 검색어")
        hint.setStyleSheet("font-size: 14px; font-weight: bold; color: #757575;")
        self._result_layout.addWidget(hint)

        keywords = ["다문화", "결혼이민", "귀화", "지원사업", "출입국", "한국어 교육"]
        row = QHBoxLayout()
        for kw in keywords:
            chip = QLabel(kw)
            chip.setStyleSheet(
                "background: white; border: 1px solid #E0E0E0; border-radius: 16px;"
                " padding: 6px 14px; color: #1565C0; font-size: 12px;"
            )
            row.addWidget(chip)
        row.addStretch()
        self._result_layout.addLayout(row)
        self._result_layout.addStretch()

    def _on_search(self, text: str) -> None:
        self._clear_results()

        # DB 쿼리로 검색
        news_results = DataProvider.search_news(keyword=text) if text.strip() else []
        law_results = DataProvider.search_laws(keyword=text) if text.strip() else []
        support_results = DataProvider.search_support(keyword=text) if text.strip() else []

        total = len(news_results) + len(law_results) + len(support_results)
        summary = QLabel(f"'{text}' 검색 결과: 총 {total}건")
        summary.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        self._result_layout.addWidget(summary)

        if total == 0:
            empty = QLabel("검색 결과가 없습니다. 다른 키워드로 시도해 보세요.")
            empty.setStyleSheet("color: #9E9E9E; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._result_layout.addWidget(empty)
        else:
            if news_results:
                self._add_section("📰 뉴스", news_results, "news")
            if law_results:
                self._add_section("⚖️ 법령", law_results, "law")
            if support_results:
                self._add_section("🏛️ 지원사업", support_results, "support")

        self._result_layout.addStretch()

    def _add_section(self, title: str, items: list[dict], kind: str) -> None:
        sec = QLabel(f"{title} ({len(items)}건)")
        sec.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #424242; padding-top: 8px;"
        )
        self._result_layout.addWidget(sec)

        for item in items:
            card = self._make_result_card(item, kind)
            self._result_layout.addWidget(card)

    def _make_result_card(self, item: dict, kind: str) -> QFrame:
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #1565C0; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        if kind == "news":
            title = QLabel(f"📰  {item['title']}")
            meta = QLabel(f"{item.get('source', '')}  ·  {item.get('published', '')}")
        elif kind == "law":
            title = QLabel(f"⚖️  {item['name']}")
            meta = QLabel(f"{item.get('category', '')}  ·  시행: {item.get('effective_date', '')}")
        else:
            title = QLabel(f"🏛️  {item['name']}")
            meta = QLabel(f"{item.get('organizer', '')}  ·  {item.get('region', '')}")

        title.setTextFormat(Qt.TextFormat.PlainText)
        meta.setTextFormat(Qt.TextFormat.PlainText)

        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        layout.addWidget(title)

        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        layout.addWidget(meta)

        card.mousePressEvent = lambda e, i=item, k=kind: self._open_detail(i, k)
        return card

    def _open_detail(self, item: dict, kind: str) -> None:
        if kind == "news":
            title = item["title"]
            meta = [
                f"📰 {item.get('source', '')}  ·  {item.get('category', '')}",
                f"📅 {item.get('published', '')}",
            ]
            body = item.get("content", item.get("summary", ""))
            url = item.get("url", "")
        elif kind == "law":
            title = item["name"]
            meta = [
                f"⚖️ {item.get('category', '')}",
                f"📅 개정 {item.get('amended_date', '')}  ·  시행 {item.get('effective_date', '')}",
            ]
            body = item.get("summary", item.get("content", ""))
            url = item.get("url", "")
        else:
            title = item["name"]
            meta = [
                f"🏛️ {item.get('organizer', '')}  ·  {item.get('region', '')}",
                f"📅 {item.get('apply_start', '')} ~ {item.get('apply_end', '')}",
                f"👥 대상: {item.get('target_group', '')}",
            ]
            body = f"💰 지원내용: {item.get('benefit', '')}\n\n📞 연락처: {item.get('contact', '')}"
            url = item.get("url", "")

        dlg = DetailDialog(title=title, meta_lines=meta, body=body, url=url, parent=self)
        dlg.exec()

    def _clear_results(self) -> None:
        while self._result_layout.count():
            child = self._result_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
