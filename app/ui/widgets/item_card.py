"""목록 아이템 카드 위젯들"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import pyqtSignal, Qt

from app.ui.styles import (
    COLORS, FONTS, TAG_STYLE_MAP, BOOKMARK_BTN_STYLE, LIST_ITEM_STYLE,
)


class _BaseCard(QFrame):
    """공통 카드 베이스"""

    clicked = pyqtSignal(int)
    bookmark_toggled = pyqtSignal(int, bool)

    def __init__(self, item_id: int, parent=None):
        super().__init__(parent)
        self._item_id = item_id
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(LIST_ITEM_STYLE)

    def mousePressEvent(self, event):
        self.clicked.emit(self._item_id)
        super().mousePressEvent(event)

    @staticmethod
    def _plain_label(text: str) -> QLabel:
        """외부 데이터용 PlainText QLabel — HTML 렌더링 방지."""
        lbl = QLabel(text)
        lbl.setTextFormat(Qt.TextFormat.PlainText)
        return lbl

    def _make_tag(self, text: str) -> QLabel:
        tag = QLabel(text)
        tag.setTextFormat(Qt.TextFormat.PlainText)
        style = TAG_STYLE_MAP.get(text, TAG_STYLE_MAP.get("정책", ""))
        tag.setStyleSheet(style)
        return tag

    def _make_bookmark_btn(self, is_bookmarked: bool) -> QPushButton:
        btn = QPushButton("⭐" if is_bookmarked else "☆")
        btn.setStyleSheet(BOOKMARK_BTN_STYLE)
        btn.setFixedSize(32, 32)
        btn.setProperty("bookmarked", is_bookmarked)
        btn.clicked.connect(self._toggle_bookmark)
        self._bookmark_btn = btn
        return btn

    def _toggle_bookmark(self) -> None:
        current = self._bookmark_btn.property("bookmarked")
        new_state = not current
        self._bookmark_btn.setProperty("bookmarked", new_state)
        self._bookmark_btn.setText("⭐" if new_state else "☆")
        self.bookmark_toggled.emit(self._item_id, new_state)


class NewsCard(_BaseCard):
    """뉴스 카드"""

    def __init__(self, data: dict, parent=None):
        super().__init__(data["id"], parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # 상단: 카테고리 + 출처 + 날짜 + 북마크
        top = QHBoxLayout()
        top.addWidget(self._make_tag(data.get("category", "")))
        source = self._plain_label(f"{data.get('source', '')}  ·  {data.get('published', '')}")
        source.setStyleSheet(f"{FONTS.small} color: {COLORS.text_hint};")
        top.addWidget(source)
        top.addStretch()
        top.addWidget(self._make_bookmark_btn(data.get("is_bookmarked", False)))
        layout.addLayout(top)

        # 제목
        title = self._plain_label(data.get("title", ""))
        title.setStyleSheet(f"{FONTS.body} font-weight: bold; color: {COLORS.text_primary};")
        title.setWordWrap(True)
        layout.addWidget(title)

        # 요약
        summary = self._plain_label(data.get("summary", ""))
        summary.setStyleSheet(f"{FONTS.caption} color: {COLORS.text_secondary};")
        summary.setWordWrap(True)
        layout.addWidget(summary)


class LawCard(_BaseCard):
    """법령 카드"""

    def __init__(self, data: dict, parent=None):
        super().__init__(data["id"], parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.addWidget(self._make_tag(data.get("category", "")))
        date_lbl = self._plain_label(f"개정 {data.get('amended_date', '')}  ·  시행 {data.get('effective_date', '')}")
        date_lbl.setStyleSheet(f"{FONTS.small} color: {COLORS.text_hint};")
        top.addWidget(date_lbl)
        top.addStretch()
        top.addWidget(self._make_bookmark_btn(data.get("is_bookmarked", False)))
        layout.addLayout(top)

        title = self._plain_label(data.get("name", ""))
        title.setStyleSheet(f"{FONTS.body} font-weight: bold; color: {COLORS.text_primary};")
        layout.addWidget(title)

        summary = self._plain_label(data.get("summary", ""))
        summary.setStyleSheet(f"{FONTS.caption} color: {COLORS.text_secondary};")
        summary.setWordWrap(True)
        layout.addWidget(summary)


class SupportCard(_BaseCard):
    """지원사업 카드"""

    def __init__(self, data: dict, parent=None):
        super().__init__(data["id"], parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.addWidget(self._make_tag(data.get("org_type", "")))
        region_lbl = self._plain_label(data.get("region", ""))
        region_lbl.setStyleSheet(f"{FONTS.small} color: {COLORS.text_secondary};")
        top.addWidget(region_lbl)
        period = self._plain_label(f"{data.get('apply_start', '')} ~ {data.get('apply_end', '')}")
        period.setStyleSheet(f"{FONTS.small} color: {COLORS.text_hint};")
        top.addWidget(period)
        top.addStretch()
        top.addWidget(self._make_bookmark_btn(data.get("is_bookmarked", False)))
        layout.addLayout(top)

        title = self._plain_label(data.get("name", ""))
        title.setStyleSheet(f"{FONTS.body} font-weight: bold; color: {COLORS.text_primary};")
        title.setWordWrap(True)
        layout.addWidget(title)

        benefit = self._plain_label(f"💰 {data.get('benefit', '')}")
        benefit.setStyleSheet(f"{FONTS.caption} color: {COLORS.success};")
        benefit.setWordWrap(True)
        layout.addWidget(benefit)

        org = self._plain_label(f"📞 {data.get('organizer', '')} ({data.get('contact', '')})")
        org.setStyleSheet(f"{FONTS.small} color: {COLORS.text_secondary};")
        layout.addWidget(org)
