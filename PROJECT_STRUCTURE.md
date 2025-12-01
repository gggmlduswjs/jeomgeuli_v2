# 점글이 프로젝트 구조 상세 설명

## 📁 전체 프로젝트 구조

```
jeomgeuli-main/
├── backend/          # Django 백엔드 서버
├── frontend/         # React 프론트엔드 앱
├── docs/             # 문서 파일
└── README.md         # 프로젝트 개요
```

---

## 🎨 Frontend 구조 (`frontend/`)

### 📂 `src/` - 소스 코드 루트

#### 📁 `app/` - 애플리케이션 설정
- **`App.tsx`**: 메인 애플리케이션 컴포넌트
  - React Router 설정 및 라우팅 정의
  - 홈 화면, 학습 인덱스 컴포넌트 포함
  - 전체 앱의 라우트 구조 관리

#### 📁 `components/` - 재사용 가능한 UI 컴포넌트

컴포넌트는 기능별로 폴더로 정리되어 있습니다:

**📁 `braille/` - 점자 관련 컴포넌트**
- **`BrailleCell.tsx`**: 단일 점자 셀(6개 점) 표시
- **`BrailleCells.tsx`**: 여러 점자 셀 그룹 표시
- **`BrailleGrid.tsx`**: 점자 그리드 레이아웃 (2x3 점자 시각화)
- **`BrailleOutputPanel.tsx`**: 점자 출력 패널 (상단 고정, 현재 출력 중인 점자 표시)
- **`BraillePanel.tsx`**: 점자 패널 컨테이너 (재생 제어 포함)
- **`BrailleRow.tsx`**: 점자 행 표시 (여러 셀을 한 줄로)
- **`BrailleStrip.tsx`**: 점자 스트립 (텍스트→점자 실시간 변환)

**📁 `ui/` - 기본 UI 컴포넌트**
- **`AnswerCard.tsx`**: AI 답변 카드 표시
- **`AppShellMobile.tsx`**: 모바일 앱 셸 레이아웃 (공통 레이아웃)
- **`BottomBar.tsx`**: 하단 네비게이션 바
- **`Card.tsx`**: 범용 카드 컴포넌트

**📁 `input/` - 입력 관련 컴포넌트**
- **`ChatLikeInput.tsx`**: 채팅 스타일 입력창 (ChatGPT 스타일, STT/TTS 통합)
- **`MicButton.tsx`**: 마이크 버튼 (STT 시작/중지)
- **`SpeechBar.tsx`**: 음성 입력 바
- **`VoiceButton.tsx`**: 음성 버튼

**📁 `system/` - 시스템/유틸리티 컴포넌트**
- **`ErrorBoundary.tsx`**: React 에러 경계 (에러 처리)
- **`HealthCheck.tsx`**: API 헬스 체크 컴포넌트
- **`DevHealth.tsx`**: 개발용 헬스 체크
- **`ToastA11y.tsx`**: 접근성 토스트 알림

**🗑️ 제거된 컴포넌트 (사용되지 않거나 중복)**
- `Braille.tsx`, `BrailleBar.tsx`, `BrailleDots.tsx`, `BrailleToggle.tsx` (통합/제거)
- `BigButton.tsx`, `HeaderBar.tsx`, `KeywordChips.tsx`, `MessageBubble.tsx`
- `MobileShell.tsx`, `QuickActions.tsx`, `StepFooter.tsx`, `SummaryCard.tsx`
- `TTSButton.tsx`, `VoiceHelp.tsx`, `BulletList.tsx` (사용되지 않음)

#### 📁 `pages/` - 페이지 컴포넌트

- **`Home.tsx`**: 홈 화면 (메인 진입점)
- **`LearnIndex.tsx`**: 학습 메뉴 인덱스
- **`LearnStep.tsx`**: 학습 단계별 화면 (자모/단어/문장)
- **`FreeConvert.tsx`**: 자유 점자 변환 페이지
- **`Quiz.tsx`**: 퀴즈/테스트 페이지
- **`Review.tsx`**: 복습 노트 페이지
- **`TestStep.tsx`**: 테스트 단계 화면
- **`Explore.tsx`**: 정보 탐색 페이지 (ChatGPT 스타일)
- **`NotFound.tsx`**: 404 페이지

#### 📁 `hooks/` - 커스텀 React 훅

- **`useSTT.ts`**: Speech-to-Text 훅
  - Web Speech API를 사용한 음성 인식
  - `start()`, `stop()`, `isListening`, `transcript` 제공
  - 한국어 음성 인식 지원

- **`useTTS.ts`**: Text-to-Speech 훅
  - Web Speech API를 사용한 음성 합성
  - `speak()`, `stop()`, `pause()`, `resume()` 제공
  - 한국어 음성 합성 지원

- **`useBrailleBLE.ts`**: 점자 BLE(Bluetooth Low Energy) 훅
  - 블루투스 점자 디스플레이 연결 관리
  - `connect()`, `disconnect()`, `isConnected` 제공

- **`useBraillePlayback.ts`**: 점자 재생 훅
  - 점자 키워드 큐 관리 및 순차 재생
  - BLE 디바이스로 점자 전송
  - `enqueueKeywords()`, `next()`, `repeat()`, `pause()` 제공

- **`useVoiceCommands.ts`**: 음성 명령 처리 훅
  - STT 결과를 명령어로 매핑
  - 홈, 뒤로, 점자 제어, 재생 제어 등 명령 처리

#### 📁 `lib/` - 라이브러리 및 유틸리티

- **`http.ts`**: HTTP 클라이언트 유틸리티
  - `get()`, `post()`, `postFormData()` 메서드 제공
  - API 베이스 URL 설정
  - `api`, `apiBase` export

- **`api.ts`**: 통합 API 함수 모음
  - **채팅/정보 탐색**: `askChat()`, `askChatWithKeywords()`, `fetchExplore()`
  - **점자 변환**: `convertBraille()`, `generateBraillePattern()`
  - **학습**: `fetchLearn()`, `analyzePassage()`
  - **복습**: `saveReview()`
  - **시험/교재**: `listTextbooks()`, `listUnits()`, `getUnit()`, `getQuestion()`, `submitAnswer()`, `startExam()`, `convertTextbook()`, `compressText()`, `getSentenceSummary()`, `analyzeGraph()`
  - **어휘**: `getTodayVocab()`, `getNews()`
  - **분석**: `logAnalytics()`
  - **기타**: `health()`, `normalizeAnswer()`

- **`braille.ts`**: 점자 변환 유틸리티
  - `localToBrailleCells()`: 로컬 점자 변환 (API 폴백)

- **`brailleSafe.ts`**: 안전한 점자 셀 처리
  - `normalizeCells()`: 다양한 형식을 Cell[]로 정규화
  - `binsToCells()`: 바이너리 문자열을 Cell[]로 변환
  - `Cell` 타입 정의

- **`brailleMap.ts`**: 점자 매핑 타입
  - `Cell` 타입 정의 (6개 점 튜플)

- **`brailleGrid.ts`**: 점자 그리드 유틸리티
  - `maskToGrid6()`: 비트마스크를 2x3 그리드로 변환

- **`normalize.ts`**: 데이터 정규화
  - `LessonItem` 타입 export

#### 📁 `store/` - 상태 관리 (Zustand)

- **`keywords.ts`**: 키워드 상태 관리
- **`lessonSession.ts`**: 학습 세션 상태 관리
  - 현재 학습 모드, 아이템, 진행 상태 저장
  - 로컬 스토리지 연동
- **`review.ts`**: 복습 데이터 상태 관리

#### 📁 `types/` - TypeScript 타입 정의

- **`index.ts`**: 주요 타입 정의
  - `Cell`, `Cells`, `DotArray`: 점자 타입
  - `LessonItem`, `LearnList`: 학습 타입
  - `ChatMessage`, `Role`: 채팅 타입
  - `TTSOptions`, `TTSHookReturn`: TTS 타입
  - `UseBraillePlaybackOptions`: 점자 재생 타입

- **`chat.ts`**: 채팅 관련 타입
- **`explore.ts`**: 탐색 관련 타입
- **`global.d.ts`**: 전역 타입 선언

#### 📁 `styles/` - 스타일 파일

- **`tokens.css`**: 디자인 토큰 (색상, 간격 등)
- **`util.css`**: 유틸리티 클래스

#### 📄 루트 파일

- **`main.tsx`**: React 앱 진입점
- **`api.ts`**: API 재export (lib/api.ts의 래퍼)
- **`index.css`**: 전역 스타일
- **`vite-env.d.ts`**: Vite 타입 정의

---

## ⚙️ Backend 구조 (`backend/`)

### 📁 `utils/` - 공통 유틸리티 (리팩토링됨)

- **`data_loader.py`**: 공통 데이터 로딩 유틸리티
  - `load_json()`: JSON 파일 안전 로드
  - `save_json()`: JSON 파일 안전 저장
  - 모든 앱에서 공통 사용

- **`braille_converter.py`**: 점자 변환 유틸리티
  - `text_to_cells()`: 텍스트→점자 셀 변환
  - 한글 자음/모음 분해 처리
  - 전역 캐시 사용

### 📁 `jeomgeuli_backend/` - Django 프로젝트 설정

- **`settings.py`**: Django 설정
  - 데이터베이스, 미들웨어, 앱 설정
  - CORS, 정적 파일 설정

- **`urls.py`**: 메인 URL 라우팅
  - `/api/*` 경로를 각 앱으로 라우팅
  - React SPA fallback 설정
  - 레거시 호환 경로 포함

- **`views.py`**: 루트 뷰 (정리됨)
  - `root_health()`: 루트 헬스 체크만 포함
  - 실제 기능은 각 앱에서 처리

- **`wsgi.py`**: WSGI 설정 (프로덕션)
- **`asgi.py`**: ASGI 설정 (비동기)
- **`middleware.py`**: 커스텀 미들웨어

### 📁 `apps/` - Django 앱들

#### 📁 `api/` - API 통합 (정리됨)
- **`urls.py`**: API 라우팅 통합
- **`views.py`**: 헬스 체크만 포함 (중복 제거)

#### 📁 `app/` - 기본 앱
- **`urls.py`**: 기본 URL
- **`views.py`**: 기본 뷰 (헬스 체크 등)

#### 📁 `chat/` - 채팅/AI 앱
- **`views.py`**: 채팅 뷰
  - `chat_ask()`: 질문 답변
  - `chat_detail()`: 자세한 설명
  - `explore()`: 정보 탐색 (뉴스 + AI) - POST/GET 모두 지원
  - `naver_news()`: 네이버 뉴스 API 프록시
  - `news_summary()`: 뉴스 요약

- **`llm.py`**: LLM 클라이언트 (OpenAI/Gemini)
- **`ai_assistant.py`**: AI 어시스턴트 로직
- **`services.py`**: 채팅 서비스 로직
- **`stream.py`**: 스트리밍 응답 처리
- **`health.py`**: 헬스 체크

#### 📁 `braille/` - 점자 변환 앱 (리팩토링됨)
- **`views.py`**: 점자 변환 뷰
  - `braille_convert()`: 텍스트→점자 변환
  - `generate_pattern()`: 점자 패턴 생성
  - `convert_formula()`: 수식 점자 변환
  - `extract_formula()`: 수식 추출
  - `utils.braille_converter` 사용 (중복 제거)
- **`services.py`**: 점자 서비스 로직

#### 📁 `learn/` - 학습 데이터 앱 (리팩토링됨)
- **`views.py`**: 학습 데이터 뷰
  - `learn_char()`: 자모 학습 데이터
  - `learn_word()`: 단어 학습 데이터
  - `learn_sentence()`: 문장 학습 데이터
  - `learn_keyword()`: 키워드 학습 데이터
  - `analyze_passage()`: 지문 분석
  - `extract_keywords()`: 핵심 키워드 추출
  - `extract_passage_key()`: 핵심 문장 추출
  - `utils.data_loader` 사용 (중복 제거)

- **`data.py`**: 데이터 로딩 유틸리티 (레거시)
- **`services.py`**: 학습 서비스 로직
- **`urls.py`**: 학습 URL 라우팅

#### 📁 `learning/` - 학습 관리 앱 (리팩토링됨)
- **`views_review.py`**: 복습 뷰
  - `review_list()`: 복습 목록 조회
  - `review_save()`: 복습 항목 저장
  - `review_enqueue()`: 복습 큐 추가
  - `review_add()`: 복습 항목 추가 (레거시)
  - `review_today()`: 오늘의 복습 (레거시)
  - DB 사용 (JSON 파일 대신)

- **`models.py`**: 데이터베이스 모델
  - `ReviewItem`: 복습 항목 모델
  - `ReviewAttempt`: 복습 시도 기록 모델
- **`repositories.py`**: 데이터 접근 계층
  - `ReviewRepository`
- **`srs.py`**: SRS(Spaced Repetition System) 알고리즘
- **`migrations/`**: 데이터베이스 마이그레이션

#### 📁 `exam/` - 시험/교재 앱 (Jeomgeuli-Suneung)
- **`views.py`**: 시험 및 교재 뷰
  - `list_textbooks()`: 교재 목록 조회
  - `upload_pdf()`: PDF 교재 업로드
  - `list_units()`: 단원 목록 조회
  - `get_unit()`: 단원 상세 조회
  - `get_question()`: 문제 상세 조회
  - `submit_answer()`: 답안 제출
  - `start_exam()`: 시험 시작
  - `analyze_graph()`: 그래프 분석
  - `convert_textbook()`: 교재 변환 (레거시)
  - `compress_text()`: 텍스트 압축
  - `get_sentence_summary()`: 문장 요약
- **`repositories.py`**: 데이터 접근 계층
  - `TextbookRepository`, `UnitRepository`, `QuestionRepository`
- **`services.py`**: 비즈니스 로직
  - `ExamSessionService`, `PassageAnalysisService`
- **`models.py`**: 데이터베이스 모델
  - `Textbook`, `Unit`, `Question`, `ExamSession`, `BrailleContent`
- **`urls.py`**: 시험 URL 라우팅

#### 📁 `vocab/` - 어휘 앱
- **`views.py`**: 어휘 뷰
  - `today_vocab()`: 오늘의 어휘 조회
  - `mark_vocab_learned()`: 어휘 학습 완료 표시
- **`repositories.py`**: 데이터 접근 계층
- **`services.py`**: 비즈니스 로직
- **`models.py`**: 데이터베이스 모델
- **`urls.py`**: 어휘 URL 라우팅

#### 📁 `explore/` - 정보 탐색 앱
- **`views.py`**: 정보 탐색 뷰
  - `get_news()`: 뉴스 피드 조회
- **`services.py`**: 비즈니스 로직
- **`urls.py`**: 탐색 URL 라우팅

#### 📁 `analytics/` - 분석 앱
- **`views.py`**: 분석 뷰
  - `log_analytics()`: 분석 데이터 로깅
- **`repositories.py`**: 데이터 접근 계층
- **`services.py`**: 비즈니스 로직
- **`models.py`**: 데이터베이스 모델
- **`urls.py`**: 분석 URL 라우팅

#### 📁 `newsfeed/` - 뉴스 피드 앱
- **`views.py`**: 뉴스 피드 뷰
- **`urls.py`**: 뉴스 URL 라우팅

#### 📁 `search/` - 검색 앱
- **`views.py`**: 검색 뷰
- **`urls.py`**: 검색 URL 라우팅

### 🔄 리팩토링 변경사항

**제거된 중복 코드:**
- `jeomgeuli_backend/views.py`의 중복 함수들 제거
- `apps/api/views.py`의 중복 구현 제거
- 각 앱의 중복 데이터 로딩 로직 제거

**통합된 기능:**
- 공통 유틸리티를 `utils/` 폴더로 통합
- 점자 변환 로직을 `utils/braille_converter.py`로 통합
- 데이터 로딩을 `utils/data_loader.py`로 통합

**책임 분리:**
- 각 앱이 자신의 책임만 담당
- 루트 뷰는 최소한의 기능만 포함
- URL 라우팅 명확화

### 📁 `data/` - 정적 참조 데이터 파일

이 폴더는 **읽기 전용 정적 데이터**만 포함합니다. 동적 데이터는 데이터베이스를 사용합니다.

#### 📄 점자 매핑 데이터 (정적 참조 데이터)
- **`ko_braille.json`**: 한글 점자 매핑 테이블
  - 문자 → 점자 셀 매핑
  - 거의 변경되지 않는 참조 데이터
  - `utils/braille_converter.py`에서 캐싱하여 사용

- **`ko_braille_core.json`**: 핵심 점자 매핑
- **`braille_catalog.json`**: 점자 카탈로그

#### 📚 학습 초기 데이터 (정적 데이터)
- **`lesson_chars.json`**: 자모 학습 데이터
  - 초성, 중성, 종성 학습 항목
  - 읽기 전용, `apps/learn/views.py`에서 로드

- **`lesson_words.json`**: 단어 학습 데이터
- **`lesson_sentences.json`**: 문장 학습 데이터
- **`lesson_keywords.json`**: 키워드 학습 데이터

#### ⚠️ 동적 데이터는 데이터베이스 사용
- ~~`review.json`~~ (레거시, 더 이상 사용 안 함)
- **`ReviewItem` 모델** (SQLite DB)
  - 복습 항목 저장
  - 동시성 보장, 트랜잭션 지원
  - SRS 알고리즘 지원
  - 사용자별 데이터 분리 가능

### 📊 데이터 관리 전략

**정적 데이터 (Static Data):**
- JSON 파일로 관리
- 거의 변경되지 않는 참조 데이터
- 빠른 로딩 필요

**동적 데이터 (Dynamic Data):**
- Django ORM 사용 (데이터베이스)
- 사용자별 데이터
- 쓰기 작업이 필요한 데이터
- 동시성 및 트랜잭션 보장

자세한 내용은 `backend/DATA_MANAGEMENT.md` 참고

### 📁 `services/` - 서비스 레이어

- **`ai.py`**: AI 서비스 로직

### 📁 `scripts/` - 실행 스크립트

- **`run_local.py`**: 로컬 실행 스크립트
- **`run_demo.py`**: 데모 실행 스크립트
- **`run_with_ngrok.py`**: ngrok 터널링 실행
- **`run_with_react_ngrok.py`**: React + ngrok 실행

### 📄 루트 파일

- **`manage.py`**: Django 관리 스크립트
- **`run.py`**: 실행 진입점
- **`requirements.txt`**: Python 의존성
- **`start_ngrok.ps1`**: ngrok 시작 스크립트 (PowerShell)

---

## 🔄 데이터 흐름

### 1. 정보 탐색 흐름
```
사용자 입력 (음성/텍스트)
  ↓
useSTT (음성 인식)
  ↓
Explore.tsx
  ↓
lib/api.ts → fetchExplore()
  ↓
POST /api/explore/
  ↓
backend/apps/chat/views.py → explore()
  ↓
AI 처리 + 뉴스 검색
  ↓
응답 반환
  ↓
AnswerCard.tsx 표시
  ↓
useTTS (음성 낭독)
  ↓
useBraillePlayback (점자 출력)
```

### 2. 점자 학습 흐름
```
LearnStep.tsx
  ↓
lib/api.ts → fetchLearn()
  ↓
GET /api/learn/{mode}/
  ↓
backend/apps/learn/views.py
  ↓
data/lesson_*.json 로드
  ↓
학습 데이터 반환
  ↓
LearnStep.tsx 표시
  ↓
lib/api.ts → convertBraille()
  ↓
POST /api/braille/convert/
  ↓
backend/apps/braille/views.py
  ↓
점자 셀 변환
  ↓
BrailleCell.tsx 표시
```

### 3. 점자 출력 흐름
```
키워드 추출
  ↓
useBraillePlayback.enqueueKeywords()
  ↓
큐에 추가
  ↓
순차 재생
  ↓
useBrailleBLE.connect()
  ↓
BLE 디바이스 연결
  ↓
점자 데이터 전송
  ↓
하드웨어 점자 디스플레이 출력
```

---

## 🛠️ 주요 기술 스택

### Frontend
- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안정성
- **Vite**: 빌드 도구
- **Tailwind CSS**: 스타일링
- **React Router**: 라우팅
- **Zustand**: 상태 관리
- **Web Speech API**: STT/TTS
- **Web Bluetooth API**: BLE 연결

### Backend
- **Django 4.2**: 웹 프레임워크
- **Django REST Framework**: REST API 지원
- **OpenAI API**: GPT 모델 (선택사항)
- **Google Gemini**: AI 모델 (기본)
- **SQLite**: 데이터베이스 (개발용)
- **CORS**: 크로스 오리진 지원
- **Repository Pattern**: 데이터 접근 계층
- **Service Layer Pattern**: 비즈니스 로직 분리

---

## 📝 주요 기능별 파일 매핑

### 음성 기능
- STT: `hooks/useSTT.ts` → Web Speech API
- TTS: `hooks/useTTS.ts` → Web Speech API
- 음성 명령: `hooks/useVoiceCommands.ts`

### 점자 기능
- 변환: `lib/api.ts` → `convertBraille()` → `backend/apps/braille/views.py`
- 표시: `components/braille/*.tsx`
- 재생: `hooks/useBraillePlayback.ts`
- BLE: `hooks/useBrailleBLE.ts`

### 학습 기능
- 데이터: `pages/LearnStep.tsx` → `lib/api.ts` → `fetchLearn()` → `backend/apps/learn/views.py`
- 퀴즈: `pages/Quiz.tsx`
- 복습: `pages/Review.tsx` → `lib/api.ts` → `saveReview()` → `backend/apps/learning/views_review.py`

### AI 기능
- 채팅: `pages/Explore.tsx` → `lib/api.ts` → `fetchExplore()` → `backend/apps/chat/views.py`
- 정보 탐색: `lib/api.ts` → `fetchExplore()` → `backend/apps/chat/views.py` 또는 `backend/apps/explore/views.py`

### 시험/교재 기능 (Jeomgeuli-Suneung)
- 교재: `pages/Textbook/Textbook.tsx` → `lib/api.ts` → `listTextbooks()` → `backend/apps/exam/views.py`
- 단원: `pages/Passage/Passage.tsx` → `lib/api.ts` → `getUnit()` → `backend/apps/exam/views.py`
- 문제: `pages/Question/Question.tsx` → `lib/api.ts` → `getQuestion()`, `submitAnswer()` → `backend/apps/exam/views.py`
- 어휘: `pages/Vocab/Vocab.tsx` → `lib/api.ts` → `getTodayVocab()` → `backend/apps/vocab/views.py`

---

이 구조는 시각장애인을 위한 접근성을 최우선으로 설계되었으며, 음성 인터페이스와 점자 출력을 통해 정보 접근성을 제공합니다.

