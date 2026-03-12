"""
데이터베이스 초기화 및 SQLAlchemy 엔진/세션 관리
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# config에서 DB 경로를 받기 전 기본값
_DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "michub.db"


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def init_db(db_path: str | None = None) -> None:
    """DB 파일을 생성하고 테이블을 초기화한다."""
    global _engine, _SessionLocal

    path = Path(db_path) if db_path else _DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

    # 모든 테이블 생성 (이미 존재하면 무시)
    from app.models import news, law, support, settings  # noqa: F401
    Base.metadata.create_all(_engine)


def get_session():
    """DB 세션을 반환한다. 사용 후 반드시 close() 호출."""
    if _SessionLocal is None:
        raise RuntimeError("init_db()를 먼저 호출하세요.")
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
