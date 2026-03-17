"""검색바 위젯"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal

from app.ui.styles import SEARCH_BAR_STYLE, get_primary_button_style


class SearchBar(QWidget):
    """검색어 입력 + 검색 버튼"""

    searched = pyqtSignal(str)  # 검색어 전달

    def __init__(self, placeholder: str = "검색어를 입력하세요...", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._input = QLineEdit()
        self._input.setPlaceholderText(placeholder)
        self._input.setStyleSheet(SEARCH_BAR_STYLE)
        self._input.returnPressed.connect(self._emit_search)
        layout.addWidget(self._input)

        btn = QPushButton("🔍 검색")
        btn.setStyleSheet(
            get_primary_button_style().replace("border-radius: 6px", "border-radius: 20px")
        )
        btn.clicked.connect(self._emit_search)
        layout.addWidget(btn)

    def _emit_search(self) -> None:
        text = self._input.text().strip()
        if text:
            self.searched.emit(text)

    def clear(self) -> None:
        self._input.clear()

    def text(self) -> str:
        return self._input.text().strip()
