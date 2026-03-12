"""북마크 뷰 — 저장된 뉴스·법령·지원사업 통합"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QTabWidget, QFrame, QHBoxLayout,
)
from PyQt6.QtCore import Qt

from app.ui.mock_data import MOCK_NEWS, MOCK_LAWS, MOCK_SUPPORT


class BookmarkView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더
        header_w = QWidget()
        header_w.setStyleSheet("background: white; border-bottom: 1px solid #E0E0E0;")
        header_layout = QVBoxLayout(header_w)
        header_layout.setContentsMargins(24, 16, 24, 16)

        header = QLabel("⭐ 북마크")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header)

        bookmarked_news = [n for n in MOCK_NEWS if n.get("is_bookmarked")]
        bookmarked_laws = [l for l in MOCK_LAWS if l.get("is_bookmarked")]
        bookmarked_support = [s for s in MOCK_SUPPORT if s.get("is_bookmarked")]
        total = len(bookmarked_news) + len(bookmarked_laws) + len(bookmarked_support)

        count = QLabel(f"총 {total}개 항목이 저장되어 있습니다")
        count.setStyleSheet("color: #757575; font-size: 12px;")
        header_layout.addWidget(count)
        layout.addWidget(header_w)

        # 탭
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                padding: 8px 20px; font-size: 13px;
                border: none; border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #1565C0; border-bottom: 2px solid #1565C0; font-weight: bold;
            }
            QTabBar::tab:!selected { color: #757575; }
        """)

        tabs.addTab(
            self._make_list(bookmarked_news, "news"),
            f"📰 뉴스 ({len(bookmarked_news)})"
        )
        tabs.addTab(
            self._make_list(bookmarked_laws, "law"),
            f"⚖️ 법령 ({len(bookmarked_laws)})"
        )
        tabs.addTab(
            self._make_list(bookmarked_support, "support"),
            f"🏛️ 지원사업 ({len(bookmarked_support)})"
        )
        layout.addWidget(tabs)

    def _make_list(self, items: list[dict], kind: str) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F5F5F5; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        if not items:
            empty = QLabel("저장된 항목이 없습니다.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #9E9E9E; padding: 40px;")
            layout.addWidget(empty)
        else:
            for item in items:
                card = self._make_card(item, kind)
                layout.addWidget(card)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _make_card(self, item: dict, kind: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #FFB300; }"
        )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)

        star = QLabel("⭐")
        star.setStyleSheet("font-size: 20px;")
        layout.addWidget(star)

        info = QVBoxLayout()
        if kind == "news":
            title = QLabel(item["title"])
            meta = QLabel(f"{item['source']}  ·  {item['published']}")
        elif kind == "law":
            title = QLabel(item["name"])
            meta = QLabel(f"{item['category']}  ·  시행: {item['effective_date']}")
        else:
            title = QLabel(item["name"])
            meta = QLabel(f"{item['organizer']}  ·  {item['region']}")

        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        info.addWidget(title)

        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        info.addWidget(meta)
        layout.addLayout(info, 1)

        return card
