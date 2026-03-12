"""법령 테이블 모델"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Law(Base):
    __tablename__ = "laws"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    law_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)  # 법제처 법령 ID
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(Text)        # 다문화/출입국/국적 등
    content: Mapped[str | None] = mapped_column(Text)          # 전문
    summary: Mapped[str | None] = mapped_column(Text)          # AI 쉬운말 요약
    amended_date: Mapped[date | None] = mapped_column(Date)    # 최종 개정일
    effective_date: Mapped[date | None] = mapped_column(Date)  # 시행일
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Law code={self.law_code!r} name={self.name!r}>"


class LawBookmarkNote(Base):
    """법령 북마크 메모"""
    __tablename__ = "law_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    law_id: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
