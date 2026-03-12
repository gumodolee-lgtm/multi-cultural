"""뉴스 테이블 모델"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str | None] = mapped_column(Text)          # 본문 첫 2문장 (저작권)
    summary: Mapped[str | None] = mapped_column(Text)          # AI 3줄 요약
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source: Mapped[str | None] = mapped_column(Text)           # 언론사명
    category: Mapped[str | None] = mapped_column(Text)         # 정책/지역/국제/사례
    published: Mapped[datetime | None] = mapped_column(DateTime)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<News id={self.id} source={self.source!r} title={self.title[:30]!r}>"
