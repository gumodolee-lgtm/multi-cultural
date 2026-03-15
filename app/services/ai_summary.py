"""
AI 요약 서비스 — 뉴스/법령 텍스트를 한국어로 요약한다.

Anthropic Claude API 사용. API 키 미설정 시 간단한 로컬 요약으로 폴백.
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.utils.config_loader import AppConfig

logger = logging.getLogger(__name__)


class AISummaryService:
    """AI 기반 텍스트 요약"""

    def __init__(self, config: AppConfig):
        self._api_key = config.anthropic_api_key
        self._enabled = bool(self._api_key)

    def summarize(self, text: str, max_length: int = 200) -> str:
        """텍스트를 요약한다.

        Args:
            text: 원문 텍스트
            max_length: 요약 최대 글자수

        Returns:
            요약된 텍스트
        """
        if not text or len(text) < 50:
            return text

        if self._enabled:
            try:
                return self._summarize_with_claude(text, max_length)
            except Exception:
                logger.exception("Claude API 요약 실패 — 로컬 요약으로 폴백")

        return self._local_summarize(text, max_length)

    def summarize_news(self, title: str, content: str) -> str:
        """뉴스 기사를 요약한다."""
        full_text = f"제목: {title}\n내용: {content}"
        return self.summarize(full_text)

    def summarize_law(self, name: str, content: str) -> str:
        """법령을 요약한다."""
        full_text = f"법령명: {name}\n조문 내용: {content}"
        return self.summarize(full_text, max_length=300)

    def _summarize_with_claude(self, text: str, max_length: int) -> str:
        """Claude API로 요약한다."""
        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"다음 텍스트를 한국어로 {max_length}자 이내로 요약해 주세요. "
                        "핵심 내용만 간결하게 작성하세요.\n\n"
                        f"{text[:3000]}"
                    ),
                }
            ],
        )
        return message.content[0].text.strip()

    @staticmethod
    def _local_summarize(text: str, max_length: int) -> str:
        """로컬 간단 요약 (API 미사용 시 폴백).

        첫 문장 + 키워드 기반으로 핵심을 추출한다.
        """
        # 줄바꿈/공백 정규화
        text = re.sub(r"\s+", " ", text).strip()

        # 문장 분리
        sentences = re.split(r"[.!?。]\s*", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return text[:max_length]

        # 중요도 키워드
        important_kw = [
            "다문화", "결혼이민", "외국인", "지원", "법률", "개정", "시행",
            "신청", "대상", "혜택", "마감", "변경", "의무", "권리",
        ]

        # 키워드 포함 문장에 가중치
        scored = []
        for i, sent in enumerate(sentences):
            score = sum(1 for kw in important_kw if kw in sent)
            # 앞쪽 문장에 약간의 보너스
            score += max(0, 3 - i) * 0.5
            scored.append((score, i, sent))

        scored.sort(key=lambda x: -x[0])

        # 상위 문장들을 원래 순서대로 조합
        top_indices = sorted([s[1] for s in scored[:3]])
        summary = ". ".join(sentences[i] for i in top_indices if i < len(sentences))

        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."

        return summary
