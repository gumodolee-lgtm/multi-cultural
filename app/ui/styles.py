"""
다문화 정보 허브 — 공통 스타일 상수
기획서 §7 UI/UX 설계 원칙 기반
"""

# 색상 팔레트
COLORS = {
    "primary": "#1565C0",
    "primary_light": "#E3F2FD",
    "primary_dark": "#0D47A1",
    "accent": "#FF8F00",
    "danger": "#D32F2F",
    "success": "#2E7D32",
    "bg": "#FFFFFF",
    "bg_light": "#F5F5F5",
    "border": "#E0E0E0",
    "text": "#212121",
    "text_secondary": "#757575",
    "text_hint": "#9E9E9E",
    "bookmark": "#FFB300",
}

# 공통 스타일시트 조각
CARD_STYLE = """
    QFrame {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    QFrame:hover {
        border-color: #1565C0;
    }
"""

LIST_ITEM_STYLE = """
    QFrame {
        background: white;
        border-bottom: 1px solid #F0F0F0;
        padding: 8px;
    }
    QFrame:hover {
        background-color: #E3F2FD;
    }
"""

TAG_STYLE_MAP = {
    "정책": "background-color: #E3F2FD; color: #1565C0; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "지역": "background-color: #E8F5E9; color: #2E7D32; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "국제": "background-color: #FFF3E0; color: #E65100; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "사례": "background-color: #F3E5F5; color: #7B1FA2; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "다문화": "background-color: #E3F2FD; color: #1565C0; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "출입국": "background-color: #FFF3E0; color: #E65100; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "국적": "background-color: #E8F5E9; color: #2E7D32; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "중앙": "background-color: #E3F2FD; color: #1565C0; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "지자체": "background-color: #E8F5E9; color: #2E7D32; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
    "민간": "background-color: #FFF3E0; color: #E65100; padding: 2px 8px; border-radius: 10px; font-size: 11px;",
}

SEARCH_BAR_STYLE = """
    QLineEdit {
        border: 2px solid #E0E0E0;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 14px;
        background: white;
    }
    QLineEdit:focus {
        border-color: #1565C0;
    }
"""

FILTER_COMBO_STYLE = """
    QComboBox {
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 4px 8px;
        min-width: 100px;
        background: white;
    }
"""

BOOKMARK_BTN_STYLE = """
    QPushButton {
        border: none;
        background: transparent;
        font-size: 18px;
        padding: 4px;
    }
    QPushButton:hover {
        background-color: #FFF8E1;
        border-radius: 4px;
    }
"""

KPI_CARD_STYLE = """
    QFrame {{
        background: {bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 16px;
    }}
"""
