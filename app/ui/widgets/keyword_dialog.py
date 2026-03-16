"""알림 키워드 관리 다이얼로그"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
)
from PyQt6.QtCore import Qt

from app.models.database import _SessionLocal
from app.models.settings import AlertKeyword
from app.utils.i18n import tr


def _get_session():
    if _SessionLocal is None:
        return None
    return _SessionLocal()


class KeywordDialog(QDialog):
    """알림 키워드를 추가/삭제하는 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("manage_keywords"))
        self.setMinimumSize(400, 350)
        self._build_ui()
        self._load_keywords()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 설명
        desc = QLabel(tr("keyword_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #616161; font-size: 12px;")
        layout.addWidget(desc)

        # 입력 행
        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText(tr("keyword_placeholder"))
        self._input.setStyleSheet(
            "QLineEdit { border: 1px solid #E0E0E0; border-radius: 6px;"
            " padding: 6px 12px; font-size: 13px; }"
            "QLineEdit:focus { border-color: #1565C0; }"
        )
        self._input.returnPressed.connect(self._add_keyword)
        input_row.addWidget(self._input, 1)

        add_btn = QPushButton(tr("keyword_add"))
        add_btn.setStyleSheet(
            "QPushButton { background: #1565C0; color: white; border: none;"
            " border-radius: 6px; padding: 6px 16px; }"
            "QPushButton:hover { background: #0D47A1; }"
        )
        add_btn.clicked.connect(self._add_keyword)
        input_row.addWidget(add_btn)
        layout.addLayout(input_row)

        # 키워드 목록
        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { border: 1px solid #E0E0E0; border-radius: 6px; }"
            "QListWidget::item { padding: 6px; }"
            "QListWidget::item:selected { background: #E3F2FD; color: #1565C0; }"
        )
        layout.addWidget(self._list, 1)

        # 하단 버튼
        btn_row = QHBoxLayout()
        del_btn = QPushButton(tr("keyword_delete"))
        del_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #D32F2F; border: 1px solid #D32F2F;"
            " border-radius: 6px; padding: 6px 16px; }"
            "QPushButton:hover { background: #FFEBEE; }"
        )
        del_btn.clicked.connect(self._delete_keyword)
        btn_row.addWidget(del_btn)

        btn_row.addStretch()

        close_btn = QPushButton(tr("close"))
        close_btn.setStyleSheet(
            "QPushButton { background: #E0E0E0; color: #424242; border: none;"
            " border-radius: 6px; padding: 6px 16px; }"
            "QPushButton:hover { background: #BDBDBD; }"
        )
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _load_keywords(self) -> None:
        """DB에서 키워드를 불러온다."""
        self._list.clear()
        session = _get_session()
        if session is None:
            return
        try:
            rows = session.query(AlertKeyword).order_by(AlertKeyword.id).all()
            for row in rows:
                item = QListWidgetItem(row.keyword)
                item.setData(Qt.ItemDataRole.UserRole, row.id)
                self._list.addItem(item)
        finally:
            session.close()

    def _add_keyword(self) -> None:
        """새 키워드를 추가한다."""
        text = self._input.text().strip()
        if not text:
            return

        session = _get_session()
        if session is None:
            return
        try:
            # 중복 확인
            exists = session.query(AlertKeyword).filter(
                AlertKeyword.keyword == text
            ).first()
            if exists:
                QMessageBox.information(
                    self, tr("manage_keywords"),
                    tr("keyword_exists"),
                )
                return

            session.add(AlertKeyword(keyword=text, enabled=True))
            session.commit()
            self._input.clear()
            self._load_keywords()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def _delete_keyword(self) -> None:
        """선택된 키워드를 삭제한다."""
        current = self._list.currentItem()
        if current is None:
            return

        kw_id = current.data(Qt.ItemDataRole.UserRole)
        session = _get_session()
        if session is None:
            return
        try:
            row = session.get(AlertKeyword, kw_id)
            if row:
                session.delete(row)
                session.commit()
            self._load_keywords()
        except Exception:
            session.rollback()
        finally:
            session.close()
