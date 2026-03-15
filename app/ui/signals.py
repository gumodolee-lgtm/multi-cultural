"""
스케줄러 → UI 시그널 브리지

APScheduler는 백그라운드 스레드에서 실행되므로, PyQt6 시그널을 통해
메인 스레드(UI)로 안전하게 이벤트를 전달한다.
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class CollectionSignal(QObject):
    """데이터 수집 완료 시그널을 발행한다.

    Attributes:
        news_collected: 뉴스 수집 완료 (수집 건수)
        laws_collected: 법령 수집 완료 (수집 건수)
        support_collected: 지원사업 수집 완료 (수집 건수)
        all_collected: 전체 수집 완료 (뉴스, 법령, 지원 각각 건수)
        error_occurred: 수집 중 오류 발생 (오류 메시지)
    """
    news_collected = pyqtSignal(int)
    laws_collected = pyqtSignal(int)
    support_collected = pyqtSignal(int)
    all_collected = pyqtSignal(int, int, int)  # news, laws, support
    error_occurred = pyqtSignal(str)
