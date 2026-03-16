"""
생활 영역 통합 뷰 — 베이스 클래스
각 영역(비자·체류, 의료·복지 등)이 이 클래스를 상속하여
관련 뉴스 + 법령 + 지원사업을 한 화면에 표시한다.
"""
from __future__ import annotations

import webbrowser
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy,
)
from PyQt6.QtCore import Qt

from app.services.data_provider import DataProvider
from app.ui.styles import COLORS
from app.ui.widgets.detail_dialog import DetailDialog


@dataclass
class AreaConfig:
    """영역별 설정"""
    key: str               # visa, health, family, education, job
    icon: str              # 이모지
    title: str             # 화면 제목
    description: str       # 한 줄 설명
    color: str             # 테마 색상
    news_keywords: list[str]
    law_keywords: list[str]
    support_keywords: list[str]


class LifeAreaView(QWidget):
    """생활 영역 통합 뷰 (베이스)"""

    def __init__(self, area: AreaConfig, parent=None):
        super().__init__(parent)
        self._area = area
        self._build_ui()

    # ------------------------------------------------------------------
    # UI 구성
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F5F5F5; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # 헤더
        header = QLabel(f"{self._area.icon}  {self._area.title}")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #212121;")
        layout.addWidget(header)

        desc = QLabel(self._area.description)
        desc.setStyleSheet("color: #757575; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 요약 카드 행
        news_items = self._filter_news()
        law_items = self._filter_laws()
        support_items = self._filter_support()

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        summary_row.addWidget(self._summary_card("📰", "관련 뉴스", len(news_items), COLORS["primary"]))
        summary_row.addWidget(self._summary_card("⚖️", "관련 법령", len(law_items), "#2E7D32"))
        summary_row.addWidget(self._summary_card("🏛️", "지원사업", len(support_items), COLORS["accent"]))
        layout.addLayout(summary_row)

        # 뉴스 섹션
        if news_items:
            layout.addWidget(self._section_title("📰 관련 뉴스"))
            for item in news_items:
                layout.addWidget(self._news_card(item))

        # 법령 섹션
        if law_items:
            layout.addWidget(self._section_title("⚖️ 관련 법령"))
            for item in law_items:
                layout.addWidget(self._law_card(item))

        # 지원사업 섹션
        if support_items:
            layout.addWidget(self._section_title("🏛️ 관련 지원사업"))
            for item in support_items:
                layout.addWidget(self._support_card(item))

        # 데이터 없음
        if not (news_items or law_items or support_items):
            empty = QLabel("아직 수집된 데이터가 없습니다.\n자동 수집이 시작되면 관련 정보가 여기에 표시됩니다.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #9E9E9E; font-size: 14px; padding: 40px;")
            layout.addWidget(empty)

        layout.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self) -> None:
        """데이터를 DB에서 다시 읽어 뷰를 갱신한다."""
        if self.layout():
            while self.layout().count():
                child = self.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            QVBoxLayout(self)
        self._build_ui()

    # ------------------------------------------------------------------
    # 데이터 필터링 (키워드 기반)
    # ------------------------------------------------------------------
    def _match(self, text: str, keywords: list[str]) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)

    def _filter_news(self) -> list[dict]:
        return DataProvider.filter_news_by_keywords(self._area.news_keywords)

    def _filter_laws(self) -> list[dict]:
        return DataProvider.filter_laws_by_keywords(self._area.law_keywords)

    def _filter_support(self) -> list[dict]:
        return DataProvider.filter_support_by_keywords(self._area.support_keywords)

    # ------------------------------------------------------------------
    # 위젯 헬퍼
    # ------------------------------------------------------------------
    def _summary_card(self, icon: str, label: str, count: int, color: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(80)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(
            f"QFrame {{ background: white; border: 1px solid #E0E0E0;"
            f" border-radius: 10px; border-left: 4px solid {color}; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        top = QLabel(f"{icon}  {label}")
        top.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(top)

        val = QLabel(str(count))
        val.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        layout.addWidget(val)

        return card

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: #212121;"
            f" padding-top: 12px; border-bottom: 2px solid {self._area.color};"
            f" padding-bottom: 4px;"
        )
        return lbl

    def _news_card(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #1565C0; }"
        )
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title = QLabel(data["title"])
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        layout.addWidget(title)

        meta = QLabel(f"{data.get('source', '')}  ·  {data.get('published', '')}  ·  {data.get('category', '')}")
        meta.setTextFormat(Qt.TextFormat.PlainText)
        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        layout.addWidget(meta)

        summary = QLabel(data.get("summary", ""))
        summary.setTextFormat(Qt.TextFormat.PlainText)
        summary.setStyleSheet("color: #616161; font-size: 12px;")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        frame.mousePressEvent = lambda e, d=data: self._open_news_detail(d)
        return frame

    def _open_news_detail(self, data: dict) -> None:
        dlg = DetailDialog(
            title=data["title"],
            meta_lines=[
                f"📰 {data.get('source', '')}  ·  {data.get('category', '')}",
                f"📅 {data.get('published', '')}",
            ],
            body=data.get("content", data.get("summary", "")),
            url=data.get("url", ""),
            parent=self,
        )
        dlg.exec()

    def _law_card(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #2E7D32; }"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title = QLabel(f"⚖️  {data['name']}")
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        layout.addWidget(title)

        meta = QLabel(f"개정 {data.get('amended_date', '')}  ·  시행 {data.get('effective_date', '')}")
        meta.setTextFormat(Qt.TextFormat.PlainText)
        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        layout.addWidget(meta)

        summary = QLabel(data.get("summary", ""))
        summary.setTextFormat(Qt.TextFormat.PlainText)
        summary.setStyleSheet("color: #616161; font-size: 12px;")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.mousePressEvent = lambda e, d=data: self._open_law_detail(d)
        return frame

    def _open_law_detail(self, data: dict) -> None:
        dlg = DetailDialog(
            title=data["name"],
            meta_lines=[
                f"⚖️ {data.get('category', '')}",
                f"📅 개정 {data.get('amended_date', '')}  ·  시행 {data.get('effective_date', '')}",
            ],
            body=data.get("summary", data.get("content", "")),
            url=data.get("url", ""),
            parent=self,
        )
        dlg.exec()

    def _support_card(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
            "QFrame:hover { border-color: #FF8F00; }"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title = QLabel(f"🏛️  {data['name']}")
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        layout.addWidget(title)

        meta_parts = [data.get("organizer", ""), data.get("region", "")]
        if data.get("apply_end"):
            meta_parts.append(f"마감: {data['apply_end']}")
        meta = QLabel("  ·  ".join(p for p in meta_parts if p))
        meta.setTextFormat(Qt.TextFormat.PlainText)
        meta.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        layout.addWidget(meta)

        benefit = QLabel(f"💰 {data.get('benefit', '')}")
        benefit.setTextFormat(Qt.TextFormat.PlainText)
        benefit.setStyleSheet("color: #2E7D32; font-size: 12px;")
        benefit.setWordWrap(True)
        layout.addWidget(benefit)

        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.mousePressEvent = lambda e, d=data: self._open_support_detail(d)
        return frame

    def _open_support_detail(self, data: dict) -> None:
        dlg = DetailDialog(
            title=data.get("name", ""),
            meta_lines=[
                f"🏛️ {data.get('organizer', '')}  ·  {data.get('region', '')}",
                f"📅 {data.get('apply_start', '')} ~ {data.get('apply_end', '')}",
                f"👥 대상: {data.get('target_group', '')}",
            ],
            body=f"💰 지원내용: {data.get('benefit', '')}\n\n📞 연락처: {data.get('contact', '')}",
            url=data.get("url", ""),
            parent=self,
        )
        dlg.exec()


# ------------------------------------------------------------------
# 5개 영역 뷰 — LifeAreaView 상속
# ------------------------------------------------------------------

class VisaAreaView(LifeAreaView):
    """🛂 비자·체류"""
    def __init__(self, parent=None):
        super().__init__(AreaConfig(
            key="visa",
            icon="🛂",
            title="비자·체류",
            description="출입국 정책, 비자 제도, 체류 자격 변경, 귀화·국적 관련 정보를 모아봅니다.",
            color="#1565C0",
            news_keywords=["출입국", "비자", "체류", "국적", "귀화", "사회통합"],
            law_keywords=["출입국", "국적", "체류", "비자"],
            support_keywords=["사회통합", "KIIP", "체류", "귀화", "국적"],
        ), parent)


class HealthAreaView(LifeAreaView):
    """⚕️ 의료·복지"""
    def __init__(self, parent=None):
        super().__init__(AreaConfig(
            key="health",
            icon="⚕️",
            title="의료·복지",
            description="의료비 지원, 건강검진, 의료 통역, 복지 서비스 관련 정보를 모아봅니다.",
            color="#2E7D32",
            news_keywords=["의료", "복지", "건강", "검진", "통역"],
            law_keywords=["의료", "복지", "건강"],
            support_keywords=["의료", "건강", "복지", "검진", "통역"],
        ), parent)


class FamilyAreaView(LifeAreaView):
    """👶 가족·육아"""
    def __init__(self, parent=None):
        super().__init__(AreaConfig(
            key="family",
            icon="👶",
            title="가족·육아",
            description="다문화가족 방문교육, 이중언어 환경, 자녀 교육 관련 정보를 모아봅니다.",
            color="#7B1FA2",
            news_keywords=["가족", "육아", "자녀", "방문교육", "이중언어", "다문화가정"],
            law_keywords=["가족", "다문화가족"],
            support_keywords=["가족", "육아", "자녀", "방문교육", "이중언어", "부모"],
        ), parent)


class EducationAreaView(LifeAreaView):
    """🎓 교육·문화"""
    def __init__(self, parent=None):
        super().__init__(AreaConfig(
            key="education",
            icon="🎓",
            title="교육·문화",
            description="한국어 교육, 문화 프로그램, 사회통합프로그램(KIIP) 관련 정보를 모아봅니다.",
            color="#E65100",
            news_keywords=["교육", "문화", "한국어", "프로그램", "사회통합"],
            law_keywords=["교육", "사회통합", "재한외국인"],
            support_keywords=["교육", "문화", "한국어", "프로그램", "사회통합"],
        ), parent)


class JobAreaView(LifeAreaView):
    """💼 일자리"""
    def __init__(self, parent=None):
        super().__init__(AreaConfig(
            key="job",
            icon="💼",
            title="일자리",
            description="취업 연계, 직업 교육, 자격증 지원, 외국인 고용 관련 정보를 모아봅니다.",
            color="#FF8F00",
            news_keywords=["일자리", "취업", "고용", "근로", "직업", "창업"],
            law_keywords=["근로자", "고용", "노동"],
            support_keywords=["취업", "직업", "자격증", "일자리", "고용", "창업"],
        ), parent)
