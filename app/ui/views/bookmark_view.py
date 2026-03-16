"""북마크 뷰 — 저장된 뉴스·법령·지원사업 통합"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QTabWidget, QFrame, QHBoxLayout,
)
from PyQt6.QtCore import Qt

from app.services.data_provider import DataProvider
from app.ui.widgets.detail_dialog import DetailDialog
from app.utils.i18n import tr


class BookmarkView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def refresh_data(self) -> None:
        """북마크 데이터를 다시 읽어 뷰를 갱신한다."""
        if self.layout():
            while self.layout().count():
                child = self.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            QVBoxLayout(self)
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

        header = QLabel(tr("bookmark_title"))
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header)

        all_news = DataProvider.get_all_news()
        all_laws = DataProvider.get_all_laws()
        all_support = DataProvider.get_all_support()
        bookmarked_news = [n for n in all_news if n.get("is_bookmarked")]
        bookmarked_laws = [l for l in all_laws if l.get("is_bookmarked")]
        bookmarked_support = [s for s in all_support if s.get("is_bookmarked")]
        total = len(bookmarked_news) + len(bookmarked_laws) + len(bookmarked_support)

        count = QLabel(tr("saved_items_count").replace("{count}", str(total)))
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
            empty = QLabel(tr("no_saved_items"))
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
        card.setCursor(Qt.CursorShape.PointingHandCursor)
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

        title.setTextFormat(Qt.TextFormat.PlainText)
        meta.setTextFormat(Qt.TextFormat.PlainText)

        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        info.addWidget(title)

        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        info.addWidget(meta)
        layout.addLayout(info, 1)

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
