"""
PDF 파서 — 다문화가족지원센터 현황 PDF를 파싱하여 DB에 저장한다.

사용자가 수동으로 다운로드한 PDF 파일을 data/ 폴더에 넣으면
해당 파일을 읽어 지원센터 정보를 추출한다.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from datetime import datetime

from sqlalchemy import select

from app.models.database import get_session
from app.models.support import SupportProgram

logger = logging.getLogger(__name__)

# 지원센터 PDF에서 찾을 패턴
_PHONE_PATTERN = re.compile(r"(\d{2,3}[)-]\s?\d{3,4}[)-]\s?\d{4})")
_REGION_KEYWORDS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
]


class PdfParser:
    """다문화가족지원센터 현황 PDF 파서"""

    def __init__(self, data_dir: str = "data"):
        self._data_dir = Path(data_dir)

    def parse_and_save(self, filename: str | None = None) -> int:
        """PDF 파일을 파싱하여 DB에 지원센터 정보를 저장한다.

        Args:
            filename: 특정 파일명. None이면 data/ 폴더에서 자동 탐색.

        Returns:
            저장된 건수
        """
        pdf_path = self._find_pdf(filename)
        if pdf_path is None:
            logger.info("다문화가족지원센터 PDF 파일 없음 — 건너뜀")
            return 0

        logger.info("PDF 파싱 시작: %s", pdf_path)

        try:
            import pdfplumber
        except ImportError:
            logger.warning("pdfplumber 미설치 — pip install pdfplumber 필요")
            return 0

        rows = self._extract_from_pdf(pdf_path)
        if not rows:
            logger.warning("PDF에서 데이터를 추출하지 못함: %s", pdf_path)
            return 0

        saved = self._save_to_db(rows)
        logger.info("PDF 파싱 완료: %d건 저장 (전체 %d행 추출)", saved, len(rows))
        return saved

    def _find_pdf(self, filename: str | None) -> Path | None:
        """data/ 폴더에서 지원센터 관련 PDF를 찾는다."""
        if filename:
            path = self._data_dir / filename
            return path if path.exists() else None

        # 자동 탐색: 다문화, 지원센터, 현황 키워드 포함 PDF
        for pdf_file in self._data_dir.glob("*.pdf"):
            name_lower = pdf_file.stem.lower()
            if any(kw in name_lower for kw in ["다문화", "지원센터", "현황"]):
                return pdf_file
        return None

    def _extract_from_pdf(self, pdf_path: Path) -> list[dict]:
        """PDF에서 테이블 데이터를 추출한다."""
        import pdfplumber

        results = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # 헤더 행으로 열 매핑 추론
                    header = [str(cell or "").strip() for cell in table[0]]
                    col_map = self._map_columns(header)

                    if not col_map.get("name"):
                        continue

                    for row in table[1:]:
                        if not row or len(row) < len(header):
                            continue
                        cells = [str(cell or "").strip() for cell in row]
                        record = self._row_to_dict(cells, col_map)
                        if record and record.get("name"):
                            results.append(record)

        return results

    def _map_columns(self, header: list[str]) -> dict[str, int]:
        """헤더 텍스트에서 열 인덱스를 매핑한다."""
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            h_lower = h.replace(" ", "")
            if any(kw in h_lower for kw in ["센터명", "기관명", "지원센터"]):
                col_map["name"] = i
            elif any(kw in h_lower for kw in ["주소", "소재지", "위치"]):
                col_map["address"] = i
            elif any(kw in h_lower for kw in ["전화", "연락처", "TEL"]):
                col_map["contact"] = i
            elif any(kw in h_lower for kw in ["시도", "지역", "권역"]):
                col_map["region"] = i
            elif any(kw in h_lower for kw in ["운영기관", "수탁기관"]):
                col_map["organizer"] = i
        return col_map

    def _row_to_dict(self, cells: list[str], col_map: dict[str, int]) -> dict | None:
        """행 데이터를 dict로 변환한다."""
        name_idx = col_map.get("name")
        if name_idx is None or name_idx >= len(cells):
            return None

        name = cells[name_idx].strip()
        if not name or name == "-":
            return None

        # 지역 추론
        region = ""
        if "region" in col_map and col_map["region"] < len(cells):
            region = cells[col_map["region"]].strip()
        if not region:
            # 주소 또는 이름에서 추론
            address = cells[col_map["address"]].strip() if "address" in col_map and col_map["address"] < len(cells) else ""
            text_for_region = name + " " + address
            for rk in _REGION_KEYWORDS:
                if rk in text_for_region:
                    region = rk
                    break
            if not region:
                region = "전국"

        contact = ""
        if "contact" in col_map and col_map["contact"] < len(cells):
            contact = cells[col_map["contact"]].strip()

        organizer = ""
        if "organizer" in col_map and col_map["organizer"] < len(cells):
            organizer = cells[col_map["organizer"]].strip()

        return {
            "name": name,
            "region": region,
            "contact": contact,
            "organizer": organizer or "여성가족부",
        }

    def _save_to_db(self, rows: list[dict]) -> int:
        """추출된 데이터를 DB에 저장한다."""
        saved = 0
        session_gen = get_session()
        session = next(session_gen)
        try:
            for row in rows:
                name = row["name"]
                exists = session.execute(
                    select(SupportProgram.id).where(
                        SupportProgram.name == name,
                        SupportProgram.organizer == row["organizer"],
                    )
                ).scalar_one_or_none()
                if exists:
                    continue

                program = SupportProgram(
                    name=name,
                    description=f"다문화가족지원센터 — {row['region']}",
                    organizer=row["organizer"],
                    org_type="중앙" if "여성가족부" in row["organizer"] else "지자체",
                    region=row["region"],
                    target_group="다문화가족",
                    benefit="다문화가족 상담, 교육, 통번역 등 종합 지원",
                    contact=row["contact"],
                    url="",
                    fetched_at=datetime.now(),
                )
                session.add(program)
                saved += 1

            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

        return saved
