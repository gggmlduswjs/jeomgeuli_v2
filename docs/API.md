# API 문서

## 개요

점글이 프로젝트의 API 엔드포인트 및 사용법을 설명합니다.

## Base URL

- 개발: `http://localhost:8000/api`
- 프로덕션: `/api` (상대 경로)

## 인증

현재 인증이 필요하지 않습니다. 향후 사용자 인증이 추가될 수 있습니다.

---

## 엔드포인트

### 1. 헬스 체크

#### `GET /api/health/`

서버 상태를 확인합니다.

**응답:**
```json
{
  "ok": true,
  "message": "Server is running"
}
```

---

### 2. 채팅 API

#### `POST /api/chat/ask/`

질문에 대한 AI 답변을 받습니다.

**요청:**
```json
{
  "query": "점자란 무엇인가요?"
}
```

**응답:**
```json
{
  "answer": "점자는 시각장애인을 위한 촉각 문자 체계입니다...",
  "keywords": ["점자", "시각장애인", "촉각"],
  "ok": true
}
```

**에러 응답:**
```json
{
  "error": "bad_request",
  "detail": "query or q is required"
}
```

---

### 3. 정보 탐색 API

#### `POST /api/explore/` 또는 `GET /api/explore/`

뉴스 검색 및 AI 기반 정보 탐색을 수행합니다.

**요청 (POST):**
```json
{
  "query": "오늘 날씨"
}
```

**요청 (GET):**
```
GET /api/explore/?query=오늘 날씨
```

**응답:**
```json
{
  "answer": "오늘 날씨는 맑고 기온은...",
  "news": [
    {
      "title": "날씨 관련 뉴스",
      "summary": "..."
    }
  ],
  "query": "오늘 날씨",
  "ok": true
}
```

**참고:** 실제 라우팅은 `/api/chat/explore/`로 연결되며, `/api/explore/`는 별도 앱(`apps/explore/`)에서도 제공됩니다.

---

### 4. 점자 변환 API

#### `POST /api/braille/convert/` 또는 `GET /api/braille/convert/`

한글 텍스트를 점자 셀로 변환합니다.

**요청 (POST):**
```json
{
  "text": "안녕하세요"
}
```

**요청 (GET):**
```
GET /api/braille/convert/?text=안녕하세요
```

**응답:**
```json
{
  "cells": [
    [1, 1, 0, 0, 1, 0],
    [1, 0, 1, 0, 1, 0],
    ...
  ],
  "ok": true
}
```

**셀 형식:**
- 각 셀은 6개의 숫자 배열로 표현됩니다.
- `[a, b, c, d, e, f]` 형식
- 각 숫자는 0(점 없음) 또는 1(점 있음)

#### `POST /api/braille/pattern/`

점자 패턴 생성 (Jeomgeuli-Suneung 기능)

#### `POST /api/braille/formula/`

수식 점자 변환

#### `POST /api/braille/extract-formula/`

수식 추출

---

### 5. 학습 데이터 API

#### `GET /api/learn/{mode}/`

학습 데이터를 조회합니다.

**경로 파라미터:**
- `mode`: `chars`, `words`, `sentences`, `keywords`

**예시:**
```
GET /api/learn/chars/
GET /api/learn/words/
GET /api/learn/sentences/
```

**응답:**
```json
{
  "mode": "chars",
  "items": [
    {
      "char": "ㄱ",
      "name": "기역",
      "cell": [1, 0, 0, 0, 0, 0],
      "tts": "기역"
    }
  ],
  "ok": true
}
```

---

### 6. 복습 API

#### `GET /api/learning/list/`

복습 목록을 조회합니다.

**응답:**
```json
{
  "items": [
    {
      "id": 1,
      "timestamp": "2024-01-01T00:00:00Z",
      "kind": "wrong",
      "payload": {
        "mode": "char",
        "expected": "기역",
        "user": "니은",
        "content": "ㄱ"
      }
    }
  ],
  "ok": true
}
```

#### `POST /api/learning/save/`

복습 항목을 저장합니다.

**요청:**
```json
{
  "kind": "wrong",
  "payload": {
    "mode": "char",
    "expected": "기역",
    "user": "니은",
    "idx": 0
  }
}
```

**응답:**
```json
{
  "ok": true
}
```

#### `POST /api/learning/enqueue/`

복습 큐에 항목 추가

---

### 7. 시험/교재 API (Jeomgeuli-Suneung)

#### `GET /api/exam/textbook/`

교재 목록 조회

**요청:**
```
GET /api/exam/textbook/?subject=국어
```

**응답:**
```json
{
  "ok": true,
  "textbooks": [
    {
      "id": 1,
      "title": "수능특강 국어 독서",
      "publisher": "EBS",
      "year": 2024,
      "subject": "국어"
    }
  ]
}
```

#### `POST /api/exam/textbook/upload-pdf/`

PDF 교재 업로드 (비동기 처리)

**요청:**
```
POST /api/exam/textbook/upload-pdf/
Content-Type: multipart/form-data

FormData: { pdf: File }
```

**응답:**
```json
{
  "ok": true,
  "textbook_id": 1,
  "unit_count": 5,
  "pdf_document_id": 1,
  "task_id": "abc-123-def",
  "message": "PDF 업로드 완료. 분석 및 점자 변환은 백그라운드에서 진행됩니다."
}
```

**에러 응답:**
```json
{
  "error": "PDF 파일이 필요합니다",
  "code": "VALIDATION_ERROR",
  "message": "PDF 파일을 업로드해주세요."
}
```

#### `GET /api/exam/textbook/{textbook_id}/units/`

단원 목록 조회

**응답:**
```json
{
  "ok": true,
  "units": [
    {
      "id": 1,
      "title": "1단원",
      "order": 1,
      "content": "단원 내용..."
    }
  ]
}
```

#### `GET /api/exam/unit/{unit_id}/`

단원 상세 조회

**응답:**
```json
{
  "ok": true,
  "unit": {
    "id": 1,
    "title": "1단원",
    "content": "단원 내용...",
    "textbook": {
      "id": 1,
      "title": "수능특강 국어 독서"
    }
  }
}
```

#### `GET /api/exam/unit/{unit_id}/braille-status/`

단원의 점자 변환 상태 조회

**응답:**
```json
{
  "ok": true,
  "status": "completed",
  "strategy": "korean",
  "chunk_count": 120,
  "converted_at": "2024-01-01T00:00:00Z"
}
```

#### `GET /api/exam/question/{question_id}/`

문제 상세 조회

**응답:**
```json
{
  "ok": true,
  "question": {
    "id": 1,
    "question_text": "문제 내용",
    "choice1": "선택지 1",
    "choice2": "선택지 2",
    "choice3": "선택지 3",
    "choice4": "선택지 4",
    "choice5": "선택지 5",
    "correct_answer": 1,
    "explanation": "해설",
    "difficulty": 2
  }
}
```

#### `POST /api/exam/submit/`

답안 제출

**요청:**
```json
{
  "question_id": 1,
  "answer": 3,
  "response_time": 5.5
}
```

**응답:**
```json
{
  "ok": true,
  "is_correct": false,
  "correct_answer": 1,
  "explanation": "해설"
}
```

#### `POST /api/exam/start/`

시험 시작

**요청:**
```json
{
  "total_questions": 30
}
```

**응답:**
```json
{
  "ok": true,
  "exam_id": 1,
  "started_at": "2024-01-01T00:00:00Z",
  "total_questions": 30,
  "status": "running"
}
```

#### `POST /api/exam/graph-analyze/`

그래프/도표 분석 (CV + LLM Hybrid)

**요청:**
```
POST /api/exam/graph-analyze/
Content-Type: multipart/form-data

FormData: { image: File, title: "그래프 제목" }
```

**응답:**
```json
{
  "ok": true,
  "patterns": {
    "trend": "increase",
    "extremum": "maximum",
    "comparison": "greater",
    "intervals": [
      {"type": "increase", "range": "0~2"},
      {"type": "decrease", "range": "2~5"}
    ],
    "semantic_description": "이 함수는 x가 0에서 2까지 증가하다가 2에서 5까지 감소합니다."
  },
  "cv_results": {
    "coordinate_system": {...},
    "curves": [...],
    "intervals": [...]
  },
  "item_id": 1
}
```

#### `POST /api/exam/convert-textbook/` (레거시)

교재 변환 (동기 처리)

#### `POST /api/exam/compress/`

텍스트 압축

#### `POST /api/exam/sentence-summary/`

문장 요약

---

### 8. 어휘 API

#### `GET /api/vocab/today/`

오늘의 어휘 조회

#### `POST /api/vocab/learned/`

어휘 학습 완료 표시

---

### 9. 뉴스 피드 API

#### `GET /api/explore/news/`

뉴스 피드 조회

---

### 10. 분석 API

#### `POST /api/analytics/log/`

분석 데이터 로깅

---

### 11. 학습 분석 API

#### `POST /api/learn/passage-analyze/`

지문 분석

#### `POST /api/learn/extract-keywords/`

핵심 키워드 추출

#### `POST /api/learn/extract-key/`

핵심 문장 추출

---

## 에러 처리

### 통일된 에러 응답 형식

모든 API는 통일된 에러 응답 형식을 사용합니다:

```json
{
  "error": "사용자 친화적 메시지",
  "code": "ERROR_CODE",
  "message": "기술적 상세 메시지",
  "details": {}
}
```

### 에러 코드

- `VALIDATION_ERROR`: 입력 검증 실패 (400)
- `NOT_FOUND`: 리소스를 찾을 수 없음 (404)
- `PDF_PROCESSING_ERROR`: PDF 처리 오류 (400)
- `BRAILLE_CONVERSION_ERROR`: 점자 변환 오류 (500)
- `AI_ANALYSIS_ERROR`: AI 분석 오류 (500)
- `INTERNAL_ERROR`: 서버 내부 오류 (500)

### 예시

**요청:**
```
POST /api/exam/textbook/upload-pdf/
```

**에러 응답:**
```json
{
  "error": "PDF 파일을 업로드해주세요.",
  "code": "VALIDATION_ERROR",
  "message": "PDF 파일이 필요합니다"
}
```

---

## 에러 처리 (레거시)

모든 API는 통일된 에러 형식을 사용합니다.

### 에러 응답 형식

```json
{
  "error": "error_code",
  "detail": "에러 상세 메시지"
}
```

### 에러 코드

- `bad_request`: 잘못된 요청 (400)
- `method_not_allowed`: 허용되지 않은 HTTP 메서드 (405)
- `too_many_requests`: 요청 제한 초과 (429)
- `internal_error`: 서버 내부 오류 (500)
- `network_error`: 네트워크 오류
- `timeout_error`: 요청 시간 초과

---

## 레이트 리밋

일부 엔드포인트는 레이트 리밋이 적용됩니다:
- `/api/chat/ask/`: IP당 1초에 1회

레이트 리밋 초과 시:
```json
{
  "error": "too_many_requests",
  "detail": "잠시 후 다시 시도해주세요."
}
```
상태 코드: `429`

---

## 프론트엔드 사용 예시

### API 함수 사용 (현재 구조)

프로젝트는 `lib/api.ts`에 통합된 API 함수들을 제공합니다.

```typescript
// API 함수 import
import { 
  fetchExplore, 
  convertBraille, 
  fetchLearn,
  saveReview,
  listTextbooks,
  getTodayVocab
} from '@/lib/api';

// 정보 탐색
const result = await fetchExplore('오늘 날씨');
console.log(result.answer);

// 점자 변환
const braille = await convertBraille('안녕하세요');
console.log(braille.cells);

// 학습 데이터 조회
const learnData = await fetchLearn('chars');

// 복습 저장
await saveReview('wrong', {
  mode: 'char',
  expected: '기역',
  user: '니은'
});

// 교재 목록 조회
const textbooks = await listTextbooks();

// 어휘 조회
const vocab = await getTodayVocab();
```

### 에러 처리

```typescript
import { fetchExplore } from '@/lib/api';
import { isAppError } from '@/types/errors';

try {
  const result = await fetchExplore('query');
} catch (error) {
  if (isAppError(error)) {
    console.error('에러:', error.userMessage);
    // 사용자에게 친화적인 메시지 표시
  }
}
```

### HTTP 클라이언트 직접 사용

```typescript
import { http } from '@/lib/http';

// GET 요청
const response = await http.get('/learn/chars/');

// POST 요청
const response = await http.post('/chat/ask/', { query: '질문' });

// FormData 전송
const formData = new FormData();
formData.append('pdf', file);
const response = await http.postFormData('/exam/textbook/upload-pdf/', formData);
```

---

## 버전 정보

- API 버전: v1
- 최종 업데이트: 2024년

## 참고사항

### 엔드포인트 라우팅

- `/api/explore/`는 두 곳에서 제공됩니다:
  - `/api/chat/explore/` (apps/chat/views.py)
  - `/api/explore/` (apps/explore/views.py)
- 대부분의 엔드포인트는 POST와 GET 모두 지원합니다.
- 점자 변환 API는 `/api/braille/convert/`와 `/api/braille/encode/` 모두 사용 가능합니다.

