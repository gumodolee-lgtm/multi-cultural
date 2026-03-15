"""
다문화 정보 허브 — 진입점
실행: python main.py
"""
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (패키지 임포트 보장)
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication

from app.utils.config_loader import load_config
from app.models.database import init_db
from app.models.seed import seed_if_empty
from app.ui.main_window import MainWindow
from app.scheduler.scheduler import CollectorScheduler


def _setup_logging() -> None:
    """로그 설정 — 콘솔 + 파일 출력"""
    log_dir = ROOT / "data"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "michub.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    # 0. 로깅 설정
    _setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=== 다문화 정보 허브 시작 ===")

    # 1. 설정 로드
    config = load_config()

    # 2. DB 초기화 (테이블 생성) + 첫 실행 시 초기 데이터 시딩
    init_db(config.db_path)
    logger.info("DB 초기화 완료: %s", config.db_path)
    seed_if_empty()

    # 3. Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName(config.name)
    app.setApplicationVersion(config.version)

    # 고DPI 스케일링 — PyQt6에서는 기본 활성화되어 별도 설정 불필요

    # 4. 메인 윈도우 생성 (시그널 객체 포함)
    window = MainWindow(config)

    # 5. 백그라운드 스케줄러 시작 (윈도우의 시그널 객체를 공유)
    scheduler = CollectorScheduler(config, signal=window.collection_signal)
    window.set_scheduler(scheduler)
    scheduler.start()

    window.update_status("자동 수집 활성화됨")
    window.show()

    # 6. 이벤트 루프 시작
    exit_code = app.exec()

    # 7. 정리
    scheduler.stop()
    logger.info("=== 다문화 정보 허브 종료 ===")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
