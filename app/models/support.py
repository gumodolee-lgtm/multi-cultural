"""지원사업 테이블 모델"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class SupportProgram(Base):
    __tablename__ = "support_programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    organizer: Mapped[str | None] = mapped_column(Text)        # 주관 기관
    org_type: Mapped[str | None] = mapped_column(Text)         # 중앙/지자체/민간
    region: Mapped[str | None] = mapped_column(Text)           # 지역 (예: "경기", "서울")
    target_group: Mapped[str | None] = mapped_column(Text)     # JSON 문자열: 대상 조건
    benefit: Mapped[str | None] = mapped_column(Text)          # 지원 내용
    apply_start: Mapped[date | None] = mapped_column(Date)
    apply_end: Mapped[date | None] = mapped_column(Date)
    contact: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<SupportProgram name={self.name!r} region={self.region!r}>"
