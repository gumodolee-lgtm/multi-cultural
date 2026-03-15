"""
PDF 파서 — 다문화가족지원센터 현황 PDF를 파싱하여 DB에 저장한다.

동작 흐름:
1. data/ 폴더에서 지원센터 관련 PDF 자동 탐색
2. 없으면 여성가족부/다누리 사이트에서 자동 다운로드 시도
3. PDF 테이블 추출 (pdfplumber) → 텍스트 폴백
4. 지원센터 정보를 DB에 upsert
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from datetime import datetime

import requests
from sqlalchemy import select

from app.models.database import get_session
from app.models.support import SupportProgram

logger = logging.getLogger(__name__)

# 지원센터 PDF에서 찾을 패턴
_PHONE_PATTERN = re.compile(r"(\d{2,4}[-)\s]?\d{3,4}[-)\s]?\d{4})")
_REGION_KEYWORDS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
]

# 다문화가족지원센터 현황 PDF 다운로드 URL 목록 (순서대로 시도)
_PDF_DOWNLOAD_URLS = [
    # 여성가족부 다문화가족지원센터 현황 (공공데이터 포털)
    "https://www.mogef.go.kr/mp/pcd/mp_pcd_s001d.do?mid=plc503&bbtSn=704916",
    # 다누리(liveinkorea) 지원센터 목록 페이지
    "https://www.liveinkorea.kr/portal/KOR/center/centerList.do",
]


class PdfParser:
    """다문화가족지원센터 현황 PDF 파서"""

    def __init__(self, data_dir: str = "data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def parse_and_save(self, filename: str | None = None) -> int:
        """PDF 파일을 파싱하여 DB에 지원센터 정보를 저장한다.

        Args:
            filename: 특정 파일명. None이면 data/ 폴더에서 자동 탐색.

        Returns:
            저장된 건수
        """
        pdf_path = self._find_pdf(filename)

        # PDF 파일이 없으면 다운로드 시도
        if pdf_path is None:
            pdf_path = self._try_download()

        if pdf_path is None:
            logger.info("다문화가족지원센터 PDF 파일 없음 — 내장 데이터 사용")
            return self._seed_builtin_centers()

        logger.info("PDF 파싱 시작: %s", pdf_path)

        try:
            import pdfplumber  # noqa: F811
        except ImportError:
            logger.warning("pdfplumber 미설치 — 내장 데이터 사용")
            return self._seed_builtin_centers()

        rows = self._extract_from_pdf(pdf_path)

        # 테이블 추출 실패 시 텍스트 기반 폴백
        if not rows:
            rows = self._extract_from_text(pdf_path)

        if not rows:
            logger.warning("PDF에서 데이터를 추출하지 못함 — 내장 데이터 사용")
            return self._seed_builtin_centers()

        saved = self._save_to_db(rows)
        logger.info("PDF 파싱 완료: %d건 저장 (전체 %d행 추출)", saved, len(rows))
        return saved

    # ------------------------------------------------------------------
    # PDF 파일 탐색 / 다운로드
    # ------------------------------------------------------------------

    def _find_pdf(self, filename: str | None) -> Path | None:
        """data/ 폴더에서 지원센터 관련 PDF를 찾는다."""
        if filename:
            path = self._data_dir / filename
            return path if path.exists() else None

        for pdf_file in self._data_dir.glob("*.pdf"):
            name_lower = pdf_file.stem.lower()
            if any(kw in name_lower for kw in ["다문화", "지원센터", "현황", "center"]):
                return pdf_file
        return None

    def _try_download(self) -> Path | None:
        """알려진 URL에서 PDF 다운로드를 시도한다."""
        for url in _PDF_DOWNLOAD_URLS:
            try:
                logger.info("PDF 다운로드 시도: %s", url)
                resp = requests.get(url, timeout=30, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                })
                resp.raise_for_status()

                # 파일 크기 제한 (50MB)
                if len(resp.content) > 50 * 1024 * 1024:
                    logger.warning("PDF 파일 크기 초과 (%d bytes) — 건너뜀", len(resp.content))
                    continue

                content_type = resp.headers.get("Content-Type", "")
                if "pdf" in content_type.lower() or resp.content[:5] == b"%PDF-":
                    save_path = self._data_dir / "다문화가족지원센터_현황.pdf"
                    save_path.write_bytes(resp.content)
                    logger.info("PDF 다운로드 완료: %s (%d bytes)", save_path, len(resp.content))
                    return save_path
                else:
                    logger.debug("PDF가 아닌 응답 (Content-Type: %s)", content_type)
            except requests.RequestException as e:
                logger.debug("PDF 다운로드 실패: %s — %s", url, e)
                continue

        logger.info("PDF 자동 다운로드 실패 — 수동 업로드 또는 내장 데이터 사용")
        return None

    # ------------------------------------------------------------------
    # PDF 추출 (테이블 기반)
    # ------------------------------------------------------------------

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

                    header = [str(cell or "").strip() for cell in table[0]]
                    col_map = self._map_columns(header)

                    if not col_map.get("name"):
                        continue

                    for row in table[1:]:
                        if not row or len(row) < 2:
                            continue
                        cells = [str(cell or "").strip() for cell in row]
                        record = self._row_to_dict(cells, col_map)
                        if record and record.get("name"):
                            results.append(record)

        return results

    # ------------------------------------------------------------------
    # PDF 추출 (텍스트 기반 폴백)
    # ------------------------------------------------------------------

    def _extract_from_text(self, pdf_path: Path) -> list[dict]:
        """테이블 추출 실패 시 텍스트에서 지원센터 정보를 추출한다."""
        import pdfplumber

        results = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines = text.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line or len(line) < 5:
                        continue

                    # "센터" 키워드가 포함된 행에서 정보 추출
                    if "센터" not in line and "지원" not in line:
                        continue

                    # 전화번호 추출
                    phone_match = _PHONE_PATTERN.search(line)
                    contact = phone_match.group(1) if phone_match else ""

                    # 지역 추론
                    region = ""
                    for rk in _REGION_KEYWORDS:
                        if rk in line:
                            region = rk
                            break

                    # 센터명 추출 (전화번호 앞부분)
                    name = line
                    if phone_match:
                        name = line[:phone_match.start()].strip()
                    # 너무 긴 이름 자르기
                    if len(name) > 50:
                        name = name[:50]

                    if name and region:
                        results.append({
                            "name": name,
                            "region": region,
                            "contact": contact,
                            "organizer": "여성가족부",
                        })

        # 중복 제거
        seen = set()
        unique = []
        for r in results:
            key = r["name"]
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    # ------------------------------------------------------------------
    # 열 매핑 / 행 변환
    # ------------------------------------------------------------------

    def _map_columns(self, header: list[str]) -> dict[str, int]:
        """헤더 텍스트에서 열 인덱스를 매핑한다."""
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            h_lower = h.replace(" ", "")
            if any(kw in h_lower for kw in ["센터명", "기관명", "지원센터", "시설명"]):
                col_map["name"] = i
            elif any(kw in h_lower for kw in ["주소", "소재지", "위치"]):
                col_map["address"] = i
            elif any(kw in h_lower for kw in ["전화", "연락처", "TEL", "tel"]):
                col_map["contact"] = i
            elif any(kw in h_lower for kw in ["시도", "지역", "권역", "시·도"]):
                col_map["region"] = i
            elif any(kw in h_lower for kw in ["운영기관", "수탁기관", "운영법인"]):
                col_map["organizer"] = i
        return col_map

    def _row_to_dict(self, cells: list[str], col_map: dict[str, int]) -> dict | None:
        """행 데이터를 dict로 변환한다."""
        name_idx = col_map.get("name")
        if name_idx is None or name_idx >= len(cells):
            return None

        name = cells[name_idx].strip()
        if not name or name == "-" or name == "합계" or name == "소계":
            return None

        # 지역 추론
        region = ""
        if "region" in col_map and col_map["region"] < len(cells):
            region = cells[col_map["region"]].strip()
        if not region:
            address = ""
            if "address" in col_map and col_map["address"] < len(cells):
                address = cells[col_map["address"]].strip()
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

    # ------------------------------------------------------------------
    # 내장 지원센터 데이터 (PDF 없을 때 폴백)
    # ------------------------------------------------------------------

    def _seed_builtin_centers(self) -> int:
        """PDF를 구할 수 없을 때 주요 지원센터 내장 데이터를 DB에 저장한다."""
        builtin = [
            {"name": "서울다문화가족지원센터", "region": "서울", "contact": "02-3675-3511", "organizer": "여성가족부"},
            {"name": "서울남부다문화가족지원센터", "region": "서울", "contact": "02-3281-9064", "organizer": "여성가족부"},
            {"name": "경기다문화가족지원센터", "region": "경기", "contact": "031-257-2988", "organizer": "여성가족부"},
            {"name": "수원다문화가족지원센터", "region": "경기", "contact": "031-257-8842", "organizer": "여성가족부"},
            {"name": "안산다문화가족지원센터", "region": "경기", "contact": "031-599-1698", "organizer": "여성가족부"},
            {"name": "부산다문화가족지원센터", "region": "부산", "contact": "051-441-5765", "organizer": "여성가족부"},
            {"name": "대구다문화가족지원센터", "region": "대구", "contact": "053-654-3417", "organizer": "여성가족부"},
            {"name": "인천다문화가족지원센터", "region": "인천", "contact": "032-510-1250", "organizer": "여성가족부"},
            {"name": "광주다문화가족지원센터", "region": "광주", "contact": "062-942-0980", "organizer": "여성가족부"},
            {"name": "대전다문화가족지원센터", "region": "대전", "contact": "042-471-4025", "organizer": "여성가족부"},
            {"name": "울산다문화가족지원센터", "region": "울산", "contact": "052-297-2373", "organizer": "여성가족부"},
            {"name": "세종다문화가족지원센터", "region": "세종", "contact": "044-864-0505", "organizer": "여성가족부"},
            {"name": "강원다문화가족지원센터", "region": "강원", "contact": "033-813-0927", "organizer": "여성가족부"},
            {"name": "충북다문화가족지원센터", "region": "충북", "contact": "043-217-6257", "organizer": "여성가족부"},
            {"name": "충남다문화가족지원센터", "region": "충남", "contact": "041-354-0175", "organizer": "여성가족부"},
            {"name": "전북다문화가족지원센터", "region": "전북", "contact": "063-246-3031", "organizer": "여성가족부"},
            {"name": "전남다문화가족지원센터", "region": "전남", "contact": "061-285-0072", "organizer": "여성가족부"},
            {"name": "경북다문화가족지원센터", "region": "경북", "contact": "054-231-3676", "organizer": "여성가족부"},
            {"name": "경남다문화가족지원센터", "region": "경남", "contact": "055-282-0724", "organizer": "여성가족부"},
            {"name": "제주다문화가족지원센터", "region": "제주", "contact": "064-723-3280", "organizer": "여성가족부"},
        ]
        return self._save_to_db(builtin)

    # ------------------------------------------------------------------
    # DB 저장
    # ------------------------------------------------------------------

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
                    description=f"다문화가족지원센터 — {row['region']}지역 다문화가족 상담·교육·통번역 종합 지원",
                    organizer=row["organizer"],
                    org_type="중앙" if "여성가족부" in row["organizer"] else "지자체",
                    region=row["region"],
                    target_group="다문화가족, 결혼이민자",
                    benefit="한국어 교육, 가족 상담, 통번역 서비스, 취업 연계, 자녀 지원",
                    contact=row["contact"],
                    url="https://www.liveinkorea.kr",
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
