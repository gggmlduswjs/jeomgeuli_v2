# 스크립트 사용 가이드

## 1. 초기 데이터 시드 (`seed_initial_data.py`)

샘플 교재, 문제, 어휘 데이터를 생성합니다.

```bash
cd backend
python scripts/seed_initial_data.py
```

**생성되는 데이터:**
- 교재 5개 (국어, 수학, 영어, 한국사, 사회문화)
- 각 교재별 단원
- 샘플 문제
- 어휘 및 시사 용어

## 2. PDF 배치 임포트 (`import_pdfs.py`)

`backend/data/pdfs/` 폴더의 모든 PDF 파일을 처리하여 Textbook/Unit 데이터로 변환합니다.

### 기본 사용법

```bash
cd backend
python scripts/import_pdfs.py
```

### AI 모드 (더 정확한 단원 추출)

```bash
cd backend
python scripts/import_pdfs.py --ai
```

**필요 사항:**
- `backend/data/pdfs/` 폴더에 PDF 파일 넣기
- AI 모드 사용 시: `.env` 파일에 `OPENAI_API_KEY` 설정 (기본값)
  - Gemini 사용 시: `DEFAULT_AI_PROVIDER=gemini`과 `GEMINI_API_KEY` 설정

**파일명 규칙:**
- `수능특강_국어_2024.pdf` 형식 권장
- 파일명에서 교재명, 과목, 연도 자동 추출

**자세한 내용:** `backend/data/pdfs/README.md` 참조

## 스크립트 실행 순서

1. **초기 데이터 생성** (선택)
   ```bash
   python scripts/seed_initial_data.py
   ```

2. **PDF 임포트** (PDF 파일이 있는 경우)
   ```bash
   python scripts/import_pdfs.py
   ```

3. **서버 실행**
   ```bash
   python manage.py runserver
   ```


