"""다문화가족실태조사 통계 테이블 모델"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class SurveyStats(Base):
    __tablename__ = "survey_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    approval_no: Mapped[str] = mapped_column(Text, nullable=False)     # 승인통계번호
    survey_name: Mapped[str] = mapped_column(Text, nullable=False)     # 통계조사명
    cycle: Mapped[str | None] = mapped_column(Text)                    # 통계주기
    survey_year: Mapped[str] = mapped_column(Text, nullable=False)     # 통계시점
    data_created: Mapped[str | None] = mapped_column(Text)             # 데이터기준일
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<SurveyStats year={self.survey_year!r} name={self.survey_name!r}>"
