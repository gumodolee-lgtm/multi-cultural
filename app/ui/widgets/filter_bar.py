"""필터 바 위젯"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import pyqtSignal

from app.ui.styles import COLORS, FONTS, FILTER_COMBO_STYLE


class FilterBar(QWidget):
    """콤보박스 기반 필터 바. filters: [(라벨, [선택지, ...])]"""

    changed = pyqtSignal()  # 필터 변경 시

    def __init__(self, filters: list[tuple[str, list[str]]], parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._combos: dict[str, QComboBox] = {}

        for label_text, options in filters:
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"{FONTS.caption} color: {COLORS.text_secondary};")
            layout.addWidget(lbl)

            combo = QComboBox()
            combo.addItems(options)
            combo.setStyleSheet(FILTER_COMBO_STYLE)
            combo.currentTextChanged.connect(lambda _: self.changed.emit())
            layout.addWidget(combo)

            self._combos[label_text] = combo

        layout.addStretch()

    def get_values(self) -> dict[str, str]:
        return {k: c.currentText() for k, c in self._combos.items()}

    def reset(self) -> None:
        for combo in self._combos.values():
            combo.setCurrentIndex(0)
