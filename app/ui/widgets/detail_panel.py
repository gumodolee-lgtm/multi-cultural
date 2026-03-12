"""상세 정보 패널 위젯"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton, QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal


class DetailPanel(QFrame):
    """우측 상세 패널 — 제목, 메타정보, 본문을 표시"""

    link_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white; border-left: 1px solid #E0E0E0;")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 빈 상태 안내
        self._empty_label = QLabel("← 항목을 선택하세요")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #9E9E9E; font-size: 16px;")
        layout.addWidget(self._empty_label)

        # 콘텐츠 영역 (스크롤)
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidget(self._content_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        self._scroll = scroll
        scroll.hide()
        layout.addWidget(scroll)

        # 하단 버튼
        self._btn_row = QHBoxLayout()
        self._link_btn = QPushButton("🔗 원문 보기")
        self._link_btn.setStyleSheet(
            "QPushButton { background: #1565C0; color: white; border: none;"
            " border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #0D47A1; }"
        )
        self._link_btn.hide()
        self._link_btn.clicked.connect(self._on_link)
        self._btn_row.addStretch()
        self._btn_row.addWidget(self._link_btn)
        layout.addLayout(self._btn_row)

        self._url = ""

    def show_detail(
        self,
        title: str,
        meta_lines: list[str],
        body: str,
        url: str = "",
    ) -> None:
        """상세 패널에 콘텐츠 표시"""
        # 기존 콘텐츠 제거
        while self._content_layout.count():
            child = self._content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._empty_label.hide()
        self._scroll.show()

        # 제목
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #212121;")
        lbl_title.setWordWrap(True)
        self._content_layout.addWidget(lbl_title)

        # 메타 정보
        for line in meta_lines:
            meta = QLabel(line)
            meta.setStyleSheet("color: #757575; font-size: 12px;")
            self._content_layout.addWidget(meta)

        # 구분선
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #E0E0E0;")
        self._content_layout.addWidget(sep)

        # 본문
        lbl_body = QLabel(body)
        lbl_body.setStyleSheet("color: #424242; font-size: 13px; line-height: 1.6;")
        lbl_body.setWordWrap(True)
        lbl_body.setTextFormat(Qt.TextFormat.PlainText)
        self._content_layout.addWidget(lbl_body)

        self._content_layout.addStretch()

        # 원문 링크
        self._url = url
        if url:
            self._link_btn.show()
        else:
            self._link_btn.hide()

    def clear(self) -> None:
        while self._content_layout.count():
            child = self._content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._scroll.hide()
        self._empty_label.show()
        self._link_btn.hide()

    def _on_link(self) -> None:
        if self._url:
            self.link_clicked.emit(self._url)
