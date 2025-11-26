# 점글이 아키텍처 문서

## 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Pages      │  │  Components  │  │    Hooks     │  │
│  │              │  │              │  │              │  │
│  │ - Home       │  │ - Braille*   │  │ - useSTT     │  │
│  │ - Explore    │  │ - Input*     │  │ - useTTS     │  │
│  │ - LearnStep  │  │ - UI*        │  │ - useVoice*  │  │
│  │ - Quiz       │  │              │  │              │  │
│  │ - Review     │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                              │
│  ┌─────────────────────────▼──────────────────────────┐  │
│  │              Services Layer                         │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │ VoiceService │  │CommandService│                │  │
│  │  └──────┬───────┘  └──────┬───────┘                │  │
│  └─────────┼──────────────────┼───────────────────────┘  │
│            │                  │                           │
│  ┌─────────▼──────────────────▼───────────────────────┐  │
│  │              State Management                      │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │         useVoiceStore (Zustand)              │ │  │
│  │  │  - isListening, transcript, alternatives    │ │  │
│  │  │  - isSpeaking, micMode                      │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Event System                          │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │         VoiceEventBus                         │ │  │
│  │  │  - MIC_MODE, TRANSCRIPT, COMMAND             │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │              API Layer (Facade Pattern)             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │  │
│  │  │  ExamAPI     │  │  ChatAPI     │  │BrailleAPI│ │  │
│  │  │  VocabAPI    │  │  LearnAPI    │  │Learning  │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │         lib/api.ts (Deprecated)               │ │  │
│  │  │  - 레거시 호환성 유지, 신규 코드는 Facade 사용 │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────┘
                            │
                            │ HTTP/REST
                            │
┌───────────────────────────▼───────────────────────────────┐
│                  Backend (Django)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Apps       │  │   Services   │  │    Utils     │  │
│  │              │  │              │  │              │  │
│  │ - chat       │  │ - Passage    │  │ - braille_   │  │
│  │ - braille    │  │   Analysis   │  │   converter  │  │
│  │ - learn      │  │ - Braille    │  │ - data_      │  │
│  │ - learning   │  │   Pattern    │  │   loader     │  │
│  │ - exam       │  │ - Exam       │  │              │  │
│  │ - vocab      │  │   Session    │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                              │
│  ┌─────────────────────────▼──────────────────────────┐  │
│  │         Repository Layer (Repository Pattern)      │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │ TextbookRepo │  │ LearnDataRepo│                │  │
│  │  │ UnitRepo     │  │ ReviewRepo   │                │  │
│  │  │ QuestionRepo │  │ VocabRepo    │                │  │
│  │  └──────────────┘  └──────────────┘                │  │
│  └─────────────────────────┬──────────────────────────┘  │
│                            │                              │
│  ┌─────────────────────────▼──────────────────────────┐  │
│  │              Data Layer                             │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │   SQLite     │  │  JSON Files  │                │  │
│  │  │  (Dynamic)   │  │  (Static)    │                │  │
│  │  └──────────────┘  └──────────────┘                │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

## 데이터 흐름

### 1. 음성 입력 흐름

```
사용자 음성 입력
    ↓
GlobalVoiceRecognition
    ↓
useSTT Hook
    ↓
VoiceService.startSTT()
    ↓
Web Speech API / Google STT
    ↓
STT 결과
    ↓
useVoiceStore.setTranscript()
    ↓
VoiceEventBus.emit(TRANSCRIPT)
    ↓
CommandService.processCommand()
    ↓
CommandRouter.route()
    ↓
핸들러 실행 (네비게이션, 제어 등)
```

### 2. 정보 탐색 흐름

```
사용자 질문 입력
    ↓
Explore.tsx
    ↓
chatAPI.fetchExplore() (Facade API)
    ↓
POST /api/explore/
    ↓
backend/apps/chat/views.py → explore()
    ↓
ExploreService (Service Layer)
    ↓
AIClientFactory → AI 처리 (OpenAI/Gemini)
    ↓
뉴스 검색 (네이버 API)
    ↓
응답 반환
    ↓
AnswerCard.tsx 표시
    ↓
useTTS → 음성 낭독
    ↓
useBraillePlayback → 점자 출력
```

### 3. 점자 변환 흐름

```
텍스트 입력
    ↓
brailleAPI.convertBraille() (Facade API)
    ↓
POST /api/braille/convert/
    ↓
backend/apps/braille/views.py
    ↓
BraillePatternService (Service Layer)
    ↓
utils/braille_converter.py
    ↓
data/ko_braille.json (매핑 테이블)
    ↓
점자 셀 배열 반환
    ↓
BrailleCell.tsx 표시
```

## 핵심 모듈

### Frontend

#### 1. VoiceService (`services/VoiceService.ts`)
- **역할**: STT/TTS 통합 관리
- **책임**:
  - STT Provider 초기화 및 관리
  - TTS Provider 초기화 및 관리
  - 음성 인식/합성 상태 관리
- **주요 메서드**:
  - `startSTT(options?)`: 음성 인식 시작
  - `stopSTT()`: 음성 인식 중지
  - `speak(text, options?)`: 음성 합성
  - `getSTTState()`: 현재 STT 상태 조회

#### 2. CommandService (`services/CommandService.ts`)
- **역할**: 음성 명령 처리 및 캐싱
- **책임**:
  - 명령어 매칭 및 라우팅
  - 명령 캐시 관리
  - 대안 명령 처리
- **주요 메서드**:
  - `processCommand(text, handlers)`: 명령 처리
  - `processCommandWithAlternatives()`: 대안 처리

#### 3. CommandRouter (`lib/voice/CommandRouter.ts`)
- **역할**: 음성 텍스트를 명령으로 변환
- **책임**:
  - 텍스트 정규화
  - 퍼지 매칭
  - 명령어 매핑
- **주요 함수**:
  - `route(text, handlers)`: 명령 라우팅

#### 4. useVoiceStore (`store/voice.ts`)
- **역할**: 음성 관련 상태 단일 소스
- **상태**:
  - STT: `isListening`, `transcript`, `alternatives`, `sttError`
  - TTS: `isSpeaking`, `isPaused`, `ttsError`
  - Mic Mode: `micMode`
- **액션**:
  - `setListening()`, `setTranscript()`, `setMicMode()`, etc.

#### 5. VoiceEventBus (`lib/voice/VoiceEventBus.ts`)
- **역할**: 이벤트 기반 통신
- **이벤트 타입**:
  - `MIC_MODE`: 마이크 모드 변경
  - `TRANSCRIPT`: 음성 인식 결과
  - `COMMAND`: 명령 실행
  - `MIC_INTENT`: 마이크 의도

### Backend

#### 1. Chat App (`apps/chat/`)
- **역할**: AI 기반 채팅 및 정보 탐색
- **주요 엔드포인트**:
  - `/api/chat/ask/`: 질문 답변
  - `/api/explore/`: 정보 탐색
- **의존성**:
  - OpenAI API
  - Google Gemini API
  - 네이버 뉴스 API

#### 2. Braille App (`apps/braille/`)
- **역할**: 점자 변환
- **주요 엔드포인트**:
  - `/api/braille/convert/`: 텍스트 → 점자 변환
- **의존성**:
  - `utils/braille_converter.py`
  - `data/ko_braille.json`

#### 3. Learn App (`apps/learn/`)
- **역할**: 학습 데이터 제공
- **주요 엔드포인트**:
  - `/api/learn/{mode}/`: 학습 데이터 조회
  - `/api/learn/passage-analyze/`: 지문 분석
  - `/api/learn/extract-keywords/`: 키워드 추출
  - `/api/learn/extract-key/`: 핵심 문장 추출
- **아키텍처**:
  - **Repository**: `LearnDataRepository` - 데이터 접근 계층
  - **Service**: `PassageAnalysisService` - 비즈니스 로직
- **데이터 소스**:
  - `data/lesson_*.json` (정적 데이터)

## 상태 관리 전략

### 단일 소스 원칙
- **음성 상태**: `useVoiceStore` (Zustand)
- **학습 세션**: `store/lessonSession.ts`
- **복습 데이터**: `store/review.ts`

### 상태 동기화
```
useVoiceStore (단일 소스)
    ↓
VoiceEventBus (이벤트 발생)
    ↓
MicMode (래퍼, 하위 호환성)
```

## 에러 처리 전략

### 통일된 에러 타입
```typescript
interface AppError {
  code: ErrorCode;
  message: string;
  userMessage: string;
  timestamp: number;
  status?: number;
}
```

### 에러 처리 흐름
```
API 호출
    ↓
HTTP 에러 발생
    ↓
toAppError() 변환
    ↓
AppError 생성
    ↓
사용자 친화적 메시지 표시
```

## 성능 최적화

### 1. 리렌더링 방지
- Zustand 선택자 사용
- `useMemo`, `useCallback` 활용
- 컴포넌트 메모이제이션

### 2. 코드 분할
- 라우트 기반 코드 분할
- 동적 import 사용

### 3. 캐싱
- 점자 변환 결과 캐싱
- 명령어 매칭 캐싱

## 보안 고려사항

### 1. CORS
- 개발: 모든 오리진 허용
- 프로덕션: 특정 도메인만 허용

### 2. 레이트 리밋
- IP 기반 요청 제한
- API 엔드포인트별 제한

### 3. 입력 검증
- 프론트엔드: 타입 검증
- 백엔드: 입력 검증 및 sanitization

## 디자인 패턴

### 1. Facade Pattern (프론트엔드 API)
- **목적**: 복잡한 API 호출을 단순화
- **구현**: `lib/api/*.ts` (ExamAPI, ChatAPI, BrailleAPI 등)
- **장점**: 
  - 일관된 에러 처리
  - 성능 모니터링 통합
  - 타입 안정성

### 2. Repository Pattern (백엔드 데이터 접근)
- **목적**: 데이터 접근 로직 캡슐화
- **구현**: `apps/*/repositories.py`
- **장점**:
  - 테스트 용이성
  - 데이터 소스 변경 용이
  - 쿼리 최적화 중앙화

### 3. Service Layer Pattern (백엔드 비즈니스 로직)
- **목적**: 비즈니스 로직과 데이터 접근 분리
- **구현**: `apps/*/services.py`
- **장점**:
  - 재사용성
  - 테스트 용이성
  - 유지보수성

### 4. Strategy Pattern (과목별 학습 전략)
- **목적**: 과목별 다른 학습 방법 적용
- **구현**: `frontend/src/strategies/subjectLearning.ts`
- **장점**:
  - 확장성
  - 유연성

## 확장성

### 1. 새로운 명령 추가
1. `CommandRouter.ts`의 `COMMAND_PHRASES`에 추가
2. `CommandHandlers` 타입에 핸들러 추가
3. 컴포넌트에서 핸들러 구현

### 2. 새로운 API 추가 (Facade Pattern)
1. `lib/api/`에 새로운 Facade 클래스 생성
2. `types/api.ts`에 타입 정의 추가
3. 백엔드에 엔드포인트 추가
4. Repository/Service Layer 구현

### 3. 새로운 Provider 추가
1. `VoiceService`에 Provider 인터페이스 구현
2. `createDefaultSTTProvider()`에 추가

### 4. 새로운 Repository 추가
1. `apps/{app}/repositories.py`에 Repository 클래스 생성
2. Service Layer에서 Repository 사용
3. View에서 Service 사용

## 테스트 전략

### 단위 테스트
- **프론트엔드**:
  - 핵심 로직: `CommandRouter`, `CommandService`
  - 에러 처리: `errors.ts`
  - Store: `voice.ts`
  - Facade API: `lib/api/*.ts`
- **백엔드**:
  - Repository: `apps/*/tests/test_repositories.py`
  - Service: `apps/*/tests/test_services.py`

### 통합 테스트
- API 호출 흐름 (Facade API 사용)
- 음성 제어 흐름
- Repository-Service-View 통합

### E2E 테스트
- 사용자 시나리오
- 접근성 테스트

## 참고 자료

- [프로젝트 구조 문서](../PROJECT_STRUCTURE.md)
- [API 문서](./API.md)
- [음성 제어 가이드](../VOICE_CONTROL_GUIDE.md)

