"""상세 정보 팝업 대화상자 — 대시보드·검색·북마크·생활영역에서 사용"""
from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton,
    QHBoxLayout, QFrame,
)
from PyQt6.QtCore import Qt

from app.ui.styles import (
    COLORS, FONTS, get_primary_button_style, get_outline_button_style,
)
from app.utils.i18n import tr


class DetailDialog(QDialog):
    """아이템 상세 정보를 팝업으로 표시하는 대화상자."""

    def __init__(
        self,
        title: str,
        meta_lines: list[str],
        body: str,
        url: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title[:60])
        self.setMinimumSize(520, 400)
        self.resize(600, 500)
        self.setStyleSheet(f"background: {COLORS.surface};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # 제목
        lbl_title = QLabel(title)
        lbl_title.setTextFormat(Qt.TextFormat.PlainText)
        lbl_title.setStyleSheet(f"{FONTS.h2} color: {COLORS.text_primary};")
        lbl_title.setWordWrap(True)
        layout.addWidget(lbl_title)

        # 메타 정보
        for line in meta_lines:
            if not line:
                continue
            meta = QLabel(line)
            meta.setTextFormat(Qt.TextFormat.PlainText)
            meta.setStyleSheet(f"{FONTS.caption} color: {COLORS.text_secondary};")
            meta.setWordWrap(True)
            layout.addWidget(meta)

        # 구분선
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {COLORS.divider};")
        layout.addWidget(sep)

        # 본문 (스크롤)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)

        lbl_body = QLabel(body if body else tr("no_content"))
        lbl_body.setTextFormat(Qt.TextFormat.PlainText)
        lbl_body.setStyleSheet(
            f"{FONTS.body} color: {COLORS.text_primary}; line-height: 1.6;"
        )
        lbl_body.setWordWrap(True)
        body_layout.addWidget(lbl_body)
        body_layout.addStretch()

        scroll.setWidget(body_widget)
        layout.addWidget(scroll, 1)

        # 하단 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if url and "example.com" not in url:
            link_btn = QPushButton(tr("view_source"))
            link_btn.setStyleSheet(get_primary_button_style())
            link_btn.clicked.connect(lambda: webbrowser.open(url))
            btn_row.addWidget(link_btn)

        close_btn = QPushButton(tr("close"))
        close_btn.setStyleSheet(get_outline_button_style(COLORS.text_secondary))
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)
