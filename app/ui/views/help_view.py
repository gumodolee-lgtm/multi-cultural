"""도움말 뷰 — 앱 사용 가이드, FAQ, 문의처 안내"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt


_FAQ = [
    {
        "q": "이 프로그램은 무엇인가요?",
        "a": "다문화 정보 허브는 다문화가족과 이주민을 위한 뉴스, 법령, 지원사업 정보를 "
             "자동으로 수집하여 한곳에서 볼 수 있게 해주는 데스크탑 앱입니다.",
    },
    {
        "q": "정보는 어디서 가져오나요?",
        "a": "뉴스는 주요 언론사 RSS 피드에서, 법령은 법제처 Open API에서, "
             "지원사업은 공공데이터포털 API에서 자동으로 수집합니다.",
    },
    {
        "q": "데이터는 얼마나 자주 업데이트되나요?",
        "a": "뉴스는 매 1시간, 법령은 24시간, 지원사업은 12시간마다 자동으로 갱신됩니다. "
             "설정 메뉴에서 주기를 변경할 수 있습니다.",
    },
    {
        "q": "'생활 영역' 메뉴는 무엇인가요?",
        "a": "비자·체류, 의료·복지, 가족·육아, 교육·문화, 일자리 등 생활 분야별로 "
             "관련 뉴스+법령+지원사업을 한눈에 볼 수 있는 통합 화면입니다.",
    },
    {
        "q": "즐겨찾기는 어떻게 사용하나요?",
        "a": "각 뉴스, 법령, 지원사업 카드의 ☆ 버튼을 누르면 즐겨찾기에 추가됩니다. "
             "즐겨찾기 메뉴에서 저장한 항목을 모아볼 수 있습니다.",
    },
    {
        "q": "오프라인에서도 사용할 수 있나요?",
        "a": "네. 한번 수집된 데이터는 로컬 데이터베이스에 저장되므로, "
             "인터넷 연결 없이도 이전에 수집한 정보를 확인할 수 있습니다.",
    },
]

_CONTACTS = [
    ("다누리 콜센터", "1577-1366", "다문화가족 상담 (13개 언어 지원)"),
    ("외국인종합안내센터", "1345", "출입국·체류·비자 상담"),
    ("정부민원안내", "110", "정부 서비스 전반 안내"),
    ("고용노동부", "1350", "외국인 근로자 고용·노동 상담"),
]


class HelpView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F5F5F5; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # 헤더
        header = QLabel("❓  도움말")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #212121;")
        layout.addWidget(header)

        sub = QLabel("앱 사용법과 자주 묻는 질문을 확인하세요.")
        sub.setStyleSheet("color: #757575; font-size: 13px;")
        layout.addWidget(sub)

        # FAQ 섹션
        layout.addWidget(self._section_title("💡 자주 묻는 질문"))
        for i, faq in enumerate(_FAQ, 1):
            layout.addWidget(self._faq_card(i, faq["q"], faq["a"]))

        # 주요 연락처
        layout.addWidget(self._section_title("📞 주요 연락처"))
        for name, number, desc in _CONTACTS:
            layout.addWidget(self._contact_card(name, number, desc))

        # 앱 정보
        layout.addWidget(self._section_title("ℹ️ 앱 정보"))
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
        )
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(4)

        for line in [
            "다문화 정보 허브 v0.1.0",
            "Python 3.12 + PyQt6",
            "데이터 출처: 법제처 Open API, 공공데이터포털, RSS 피드",
        ]:
            lbl = QLabel(line)
            lbl.setStyleSheet("color: #616161; font-size: 12px;")
            info_layout.addWidget(lbl)

        layout.addWidget(info_frame)

        layout.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #212121;"
            " padding-top: 12px; border-bottom: 2px solid #1565C0; padding-bottom: 4px;"
        )
        return lbl

    def _faq_card(self, num: int, question: str, answer: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        q_lbl = QLabel(f"Q{num}. {question}")
        q_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1565C0;")
        q_lbl.setWordWrap(True)
        layout.addWidget(q_lbl)

        a_lbl = QLabel(answer)
        a_lbl.setStyleSheet("color: #424242; font-size: 13px;")
        a_lbl.setWordWrap(True)
        layout.addWidget(a_lbl)

        return frame

    def _contact_card(self, name: str, number: str, desc: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(2)

        title = QLabel(f"📞  {name}  —  {number}")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        layout.addWidget(title)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(desc_lbl)

        return frame
