"""
다문화 정보 허브 — 전역 디자인 시스템
Material Design 3 기반, 접근성(WCAG AA) 명도 대비 준수

사용법:
  from app.ui.styles import COLORS, FONTS, get_card_style, ...
  또는
  from app.ui import styles
  styles.COLORS.primary
"""
from __future__ import annotations


# ═══════════════════════════════════════════════════════════════════
# 1. 색상 팔레트 (Color Palette)
# ═══════════════════════════════════════════════════════════════════

class COLORS:
    # 주요 브랜드 색상
    primary = "#1565C0"          # Blue 800 — 사이드바·버튼·링크
    primary_light = "#E3F2FD"    # Blue 50  — 호버·선택 배경
    primary_dark = "#0D47A1"     # Blue 900 — 누름 상태

    # 보조 / 강조
    accent = "#FF8F00"           # Amber 800  — 마감·긴급
    secondary = "#FF8F00"        # alias
    success = "#2E7D32"          # Green 800  — 법률·완료·혜택
    danger = "#D32F2F"           # Red 700    — 오류·삭제
    info = "#7B1FA2"             # Purple 700 — 마감임박
    bookmark = "#FFB300"         # Amber 600  — 북마크 아이콘

    # 표면 & 배경
    background = "#F5F7FA"       # 앱 전체 배경 (약간 블루틴트)
    surface = "#FFFFFF"          # 카드·패널 표면
    divider = "#E0E0E0"         # 구분선·테두리
    border_light = "#F0F0F0"     # 얇은 구분선

    # 텍스트 (WCAG AA 대비율 충족)
    text_primary = "#212121"     # Grey 900 — 제목·본문
    text_secondary = "#757575"   # Grey 600 — 부가 정보
    text_hint = "#9E9E9E"        # Grey 500 — 플레이스홀더
    text_disabled = "#BDBDBD"    # Grey 400 — 비활성
    text_on_primary = "#FFFFFF"  # 파란 배경 위 흰 글씨


# ═══════════════════════════════════════════════════════════════════
# 2. 타이포그래피 (Typography Scale)
# ═══════════════════════════════════════════════════════════════════

class FONTS:
    h1 = "font-size: 22px; font-weight: bold;"
    h2 = "font-size: 18px; font-weight: bold;"
    h3 = "font-size: 16px; font-weight: bold;"
    body = "font-size: 14px;"
    caption = "font-size: 12px;"
    small = "font-size: 11px;"


# ═══════════════════════════════════════════════════════════════════
# 3. 카드 / 아이템 공통 스타일
# ═══════════════════════════════════════════════════════════════════

def get_card_style(hover_color: str = COLORS.primary) -> str:
    """카드 프레임 — 흰 배경 + 둥근 모서리 + 호버 시 테두리 강조"""
    return f"""
        QFrame {{
            background-color: {COLORS.surface};
            border: 1px solid {COLORS.divider};
            border-radius: 8px;
        }}
        QFrame:hover {{
            border: 1px solid {hover_color};
        }}
    """


CARD_STYLE = get_card_style()

LIST_ITEM_STYLE = f"""
    QFrame {{
        background: {COLORS.surface};
        border-bottom: 1px solid {COLORS.border_light};
        padding: 8px;
    }}
    QFrame:hover {{
        background-color: {COLORS.primary_light};
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# 5. 태그 스타일 맵 (뉴스·법령·지원 카테고리 태그)
# ═══════════════════════════════════════════════════════════════════

def _tag(bg: str, fg: str) -> str:
    return (
        f"background-color: {bg}; color: {fg};"
        " padding: 2px 10px; border-radius: 10px; font-size: 11px; font-weight: bold;"
    )

TAG_STYLE_MAP: dict[str, str] = {
    "정책":   _tag("#E3F2FD", "#1565C0"),
    "다문화": _tag("#E3F2FD", "#1565C0"),
    "중앙":   _tag("#E3F2FD", "#1565C0"),
    "지역":   _tag("#E8F5E9", "#2E7D32"),
    "국적":   _tag("#E8F5E9", "#2E7D32"),
    "지자체": _tag("#E8F5E9", "#2E7D32"),
    "국제":   _tag("#FFF3E0", "#E65100"),
    "출입국": _tag("#FFF3E0", "#E65100"),
    "민간":   _tag("#FFF3E0", "#E65100"),
    "사례":   _tag("#F3E5F5", "#7B1FA2"),
}


# ═══════════════════════════════════════════════════════════════════
# 6. 입력 / 필터 / 버튼 스타일
# ═══════════════════════════════════════════════════════════════════

SEARCH_BAR_STYLE = f"""
    QLineEdit {{
        border: 2px solid {COLORS.divider};
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 14px;
        background: {COLORS.surface};
        color: {COLORS.text_primary};
    }}
    QLineEdit:focus {{
        border-color: {COLORS.primary};
    }}
    QLineEdit::placeholder {{
        color: {COLORS.text_hint};
    }}
"""

FILTER_COMBO_STYLE = f"""
    QComboBox {{
        border: 1px solid {COLORS.divider};
        border-radius: 6px;
        padding: 5px 10px;
        min-width: 100px;
        background: {COLORS.surface};
        color: {COLORS.text_primary};
        font-size: 13px;
    }}
    QComboBox:hover {{
        border-color: {COLORS.primary};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
"""

BOOKMARK_BTN_STYLE = f"""
    QPushButton {{
        border: none;
        background: transparent;
        font-size: 18px;
        padding: 4px;
        border-radius: 4px;
    }}
    QPushButton:hover {{
        background-color: #FFF8E1;
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# 7. KPI 카드 / 통계
# ═══════════════════════════════════════════════════════════════════

def get_kpi_card_style(accent_color: str) -> str:
    """KPI 카드 — 왼쪽 액센트 보더 + 그림자 효과"""
    return f"""
        QFrame {{
            background: {COLORS.surface};
            border: 1px solid {COLORS.divider};
            border-radius: 12px;
            border-left: 4px solid {accent_color};
        }}
    """

KPI_CARD_STYLE = """
    QFrame {{
        background: {bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 16px;
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# 8. 섹션 / 레이아웃 헬퍼
# ═══════════════════════════════════════════════════════════════════

def get_section_title_style(color: str = COLORS.primary) -> str:
    """섹션 제목 — 하단 라인 액센트"""
    return f"""
        font-size: 16px;
        font-weight: bold;
        color: {COLORS.text_primary};
        padding-top: 12px;
        border-bottom: 2px solid {color};
        padding-bottom: 4px;
    """


def get_primary_button_style() -> str:
    """주요 액션 버튼 (배경색 있음)"""
    return f"""
        QPushButton {{
            background: {COLORS.primary};
            color: {COLORS.text_on_primary};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {COLORS.primary_dark};
        }}
        QPushButton:pressed {{
            background: #0B3D91;
        }}
    """


def get_outline_button_style(color: str = COLORS.primary) -> str:
    """보조 액션 버튼 (테두리만)"""
    return f"""
        QPushButton {{
            background: transparent;
            color: {color};
            border: 1px solid {color};
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background: {COLORS.primary_light};
        }}
    """


def get_danger_button_style() -> str:
    """위험 액션 버튼"""
    return f"""
        QPushButton {{
            background: transparent;
            color: {COLORS.danger};
            border: 1px solid {COLORS.danger};
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background: #FFEBEE;
        }}
    """


def get_tab_style() -> str:
    """탭 위젯 스타일"""
    return f"""
        QTabWidget::pane {{
            border: none;
            background-color: {COLORS.background};
        }}
        QTabBar::tab {{
            padding: 10px 24px;
            font-size: 14px;
            font-weight: bold;
            color: {COLORS.text_secondary};
            background-color: transparent;
            border: none;
            border-bottom: 3px solid transparent;
        }}
        QTabBar::tab:selected {{
            color: {COLORS.primary};
            border-bottom: 3px solid {COLORS.primary};
        }}
        QTabBar::tab:hover:!selected {{
            color: {COLORS.text_primary};
        }}
    """


def get_scroll_area_style() -> str:
    """스크롤 영역 기본 스타일"""
    return f"""
        QScrollArea {{
            border: none;
            background: {COLORS.background};
        }}
    """


def get_header_bar_style() -> str:
    """뷰 상단 헤더 바"""
    return f"""
        background: {COLORS.surface};
        border-bottom: 1px solid {COLORS.divider};
    """


def get_group_box_style() -> str:
    """설정 그룹 박스"""
    return f"""
        QGroupBox {{
            background: {COLORS.surface};
            border: 1px solid {COLORS.divider};
            border-radius: 8px;
            padding: 16px;
            margin-top: 8px;
            font-size: 14px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: {COLORS.primary};
        }}
    """
