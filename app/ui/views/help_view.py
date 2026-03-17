"""도움말 뷰 — 앱 사용 가이드, FAQ, 문의처 안내"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt

from app.ui import styles
from app.utils.i18n import tr


# FAQ 항목: (question_key, answer_key)
_FAQ_KEYS = [
    ("faq_q1", "faq_a1"),
    ("faq_q2", "faq_a2"),
    ("faq_q3", "faq_a3"),
    ("faq_q4", "faq_a4"),
    ("faq_q5", "faq_a5"),
    ("faq_q6", "faq_a6"),
]

# 연락처: (name_key, number, desc_key)
_CONTACT_KEYS = [
    ("contact_danuri", "1577-1366", "contact_danuri_desc"),
    ("contact_foreigner", "1345", "contact_foreigner_desc"),
    ("contact_gov", "110", "contact_gov_desc"),
    ("contact_labor", "1350", "contact_labor_desc"),
]


class HelpView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {styles.COLORS.background}; }}")

        self._rebuild_content()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

    def refresh_data(self) -> None:
        """언어 전환 시 뷰를 재구성한다."""
        if self._scroll is not None:
            old = self._scroll.widget()
            if old:
                old.deleteLater()
            self._rebuild_content()

    def _rebuild_content(self) -> None:
        """스크롤 내부 컨텐츠를 (재)구성한다."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # 헤더
        header = QLabel(tr("help_title"))
        header.setStyleSheet(f"{styles.FONTS.h1} color: {styles.COLORS.text_primary};")
        layout.addWidget(header)

        sub = QLabel(tr("help_subtitle"))
        sub.setStyleSheet(f"color: {styles.COLORS.text_secondary}; {styles.FONTS.body}")
        layout.addWidget(sub)

        # FAQ 섹션
        layout.addWidget(self._section_title(tr("faq_section")))
        for i, (q_key, a_key) in enumerate(_FAQ_KEYS, 1):
            layout.addWidget(self._faq_card(i, tr(q_key), tr(a_key)))

        # 주요 연락처
        layout.addWidget(self._section_title(tr("contacts_section")))
        for name_key, number, desc_key in _CONTACT_KEYS:
            layout.addWidget(self._contact_card(tr(name_key), number, tr(desc_key)))

        # 앱 정보
        layout.addWidget(self._section_title(tr("app_info_section")))
        info_frame = QFrame()
        info_frame.setStyleSheet(styles.get_card_style())
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(4)

        for line in [
            tr("app_version"),
            "Python 3.12 + PyQt6",
            tr("app_data_source"),
        ]:
            lbl = QLabel(line)
            lbl.setStyleSheet(f"color: {styles.COLORS.text_secondary}; {styles.FONTS.caption}")
            info_layout.addWidget(lbl)

        layout.addWidget(info_frame)

        layout.addStretch()
        self._scroll.setWidget(container)

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(styles.get_section_title_style())
        return lbl

    def _faq_card(self, num: int, question: str, answer: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(styles.get_card_style())
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        q_lbl = QLabel(f"Q{num}. {question}")
        q_lbl.setStyleSheet(f"{styles.FONTS.body} font-weight: bold; color: {styles.COLORS.primary};")
        q_lbl.setWordWrap(True)
        layout.addWidget(q_lbl)

        a_lbl = QLabel(answer)
        a_lbl.setStyleSheet(f"color: {styles.COLORS.text_primary}; {styles.FONTS.body}")
        a_lbl.setWordWrap(True)
        layout.addWidget(a_lbl)

        return frame

    def _contact_card(self, name: str, number: str, desc: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(styles.get_card_style())
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(2)

        title = QLabel(f"📞  {name}  —  {number}")
        title.setStyleSheet(f"{styles.FONTS.body} font-weight: bold; color: {styles.COLORS.text_primary};")
        layout.addWidget(title)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"color: {styles.COLORS.text_secondary}; {styles.FONTS.caption}")
        layout.addWidget(desc_lbl)

        return frame
