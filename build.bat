@echo off
REM ============================================================
REM 다문화 정보 허브 — Windows 빌드 스크립트
REM 사전 조건: Python 3.12, pip install pyinstaller
REM 실행: build.bat
REM ============================================================

echo ===================================
echo  다문화 정보 허브 빌드 시작
echo ===================================

REM 1. 의존성 설치
echo [1/4] 의존성 설치...
pip install -r requirements.txt
pip install pyinstaller

REM 2. 이전 빌드 정리
echo [2/4] 이전 빌드 정리...
if exist "dist\michub" rmdir /s /q "dist\michub"
if exist "build\michub" rmdir /s /q "build\michub"

REM 3. PyInstaller 빌드
echo [3/4] PyInstaller 빌드...
pyinstaller michub.spec --noconfirm

REM 4. data 폴더 생성 (DB 저장용)
echo [4/4] 데이터 폴더 생성...
if not exist "dist\michub\data" mkdir "dist\michub\data"

REM .env 템플릿 복사
if not exist "dist\michub\.env" (
    echo # 다문화 정보 허브 환경 설정> "dist\michub\.env"
    echo PUBLIC_DATA_API_KEY=>> "dist\michub\.env"
    echo MULTICULTURAL_SURVEY_API_KEY=>> "dist\michub\.env"
    echo LAW_API_OC=test>> "dist\michub\.env"
    echo ANTHROPIC_API_KEY=>> "dist\michub\.env"
)

echo.
echo ===================================
echo  빌드 완료!
echo  실행 파일: dist\michub\michub.exe
echo ===================================
pause
