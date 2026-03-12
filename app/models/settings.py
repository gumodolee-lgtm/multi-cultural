"""앱 설정 및 알림 키워드 테이블 모델"""
from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class AppSetting(Base):
    """key-value 형태의 앱 설정 저장"""
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)


class AlertKeyword(Base):
    """사용자가 등록한 알림 키워드"""
    __tablename__ = "alert_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
