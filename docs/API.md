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

#### `POST /api/explore/`

뉴스 검색 및 AI 기반 정보 탐색을 수행합니다.

**요청:**
```json
{
  "query": "오늘 날씨"
}
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

---

### 4. 점자 변환 API

#### `POST /api/braille/convert/`

한글 텍스트를 점자 셀로 변환합니다.

**요청:**
```json
{
  "text": "안녕하세요"
}
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

---

## 에러 처리

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

### Facade API 사용 (권장)

프로젝트는 Facade Pattern을 사용하여 API 호출을 단순화했습니다. 각 도메인별 Facade API를 사용하세요.

```typescript
// Facade API import
import { chatAPI } from '@/lib/api/ChatAPI';
import { brailleAPI } from '@/lib/api/BrailleAPI';
import { examAPI } from '@/lib/api/ExamAPI';
import { learnAPI } from '@/lib/api/LearnAPI';
import { learningAPI } from '@/lib/api/LearningAPI';
import { vocabAPI } from '@/lib/api/VocabAPI';

// 정보 탐색
const result = await chatAPI.fetchExplore('오늘 날씨');
console.log(result.answer);

// 점자 변환
const braille = await brailleAPI.convertBraille('안녕하세요');
console.log(braille.cells);

// 교재 목록 조회
const textbooks = await examAPI.listTextbooks();

// 학습 데이터 조회
const learnData = await learnAPI.fetchLearn('chars');

// 어휘 조회
const vocab = await vocabAPI.getTodayVocab();
```

### 레거시 API (Deprecated)

`lib/api.ts`의 레거시 함수들은 더 이상 사용하지 않습니다. Facade API로 마이그레이션하세요.

```typescript
// ❌ 사용하지 않음
import { fetchExplore, convertBraille } from '@/lib/api';

// ✅ 권장
import { chatAPI } from '@/lib/api/ChatAPI';
import { brailleAPI } from '@/lib/api/BrailleAPI';
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

---

## 버전 정보

- API 버전: v1
- 최종 업데이트: 2024년

