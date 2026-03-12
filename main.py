"""
다문화 정보 허브 — 진입점
실행: python main.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (패키지 임포트 보장)
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app.utils.config_loader import load_config
from app.models.database import init_db
from app.ui.main_window import MainWindow


def main() -> None:
    # 1. 설정 로드
    config = load_config()

    # 2. DB 초기화 (테이블 생성)
    init_db(config.db_path)

    # 3. Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName(config.name)
    app.setApplicationVersion(config.version)

    # 고DPI 스케일링 — PyQt6에서는 기본 활성화되어 별도 설정 불필요

    # 4. 메인 윈도우 생성 및 표시
    window = MainWindow(config)
    window.show()

    # 5. 이벤트 루프 시작
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
