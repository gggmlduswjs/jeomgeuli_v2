# 점글이 (Jeomgeuli) - 시각장애인 정보접근 PWA

점글이는 시각장애인을 위한 정보접근 및 점자학습 PWA(Progressive Web App)입니다. React 프론트엔드와 Django 백엔드를 통해 음성 인터페이스, 점자 출력, AI 기반 정보 처리를 제공합니다.

## 주요 기능

### 정보탐색 모듈
- **뉴스 요약**: 최신 뉴스를 5개 카드 형태로 요약
- **쉬운 설명**: 복잡한 개념을 불릿 포인트와 쉬운 말로 설명
- **질문답변**: 일반적인 질문에 대한 AI 답변
- **음성 인터페이스**: STT/TTS를 통한 음성 상호작용
- **점자 출력**: 핵심 키워드를 점자로 순차 출력

### 점자학습 모듈
- **자모 학습**: 한글 자모의 점자 패턴 학습
- **단어 학습**: 단어 단위 점자 학습
- **문장 학습**: 문장 단위 점자 학습
- **자유 변환**: 사용자 입력 텍스트의 점자 변환
- **자동 테스트**: 학습 내용에 대한 자동 평가
- **복습 노트**: 오답 문제 자동 저장 및 복습

## 기술 스택

### Frontend
- **React 18** + **TypeScript**
- **Vite** (빌드 도구)
- **Tailwind CSS** (스타일링)
- **React Query** (데이터 페칭)
- **Zustand** (상태 관리)
- **React Router** (라우팅)
- **PWA** (Progressive Web App)

### Backend
- **Django 4.2** + **Django REST Framework**
- **Google Gemini AI** (정보 처리)
- **SQLite** (개발용 데이터베이스)
- **CORS** (크로스 오리진 지원)

### 음성 기능
- **Web Speech API** (STT/TTS)
- **한국어 음성 인식/합성**

## 설치 및 실행

### 사전 요구사항
- Node.js 18+
- Python 3.8+
- Google Gemini API Key

### PWA 설치 (모바일)
- **Android**: Chrome에서 사이트 접속 후 "홈 화면에 추가"
- **iOS**: Safari에서 사이트 접속 후 "홈 화면에 추가"
- 자세한 내용: [PWA 설치 가이드](./docs/PWA_SETUP.md)

### 하드웨어 연동 (점자 디스플레이)
- BLE 점자 디스플레이와 연동 가능
- 상용 제품 사용: [하드웨어 연동 가이드](./docs/HARDWARE_INTEGRATION.md)
- 직접 제작: [Arduino 펌웨어 개발 가이드](./docs/ARDUINO_FIRMWARE.md)

### 1. 저장소 클론
\`\`\`bash
git clone <repository-url>
cd jeomgeuli
\`\`\`

### 2. 백엔드 설정
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 GEMINI_API_KEY 설정

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
\`\`\`

### 3. 프론트엔드 설정
\`\`\`bash
cd frontend
npm install

# 개발 서버 실행
npm run dev
\`\`\`

### 4. 접속
- 프론트엔드: http://localhost:5173 (Vite 기본 포트)
- 백엔드 API: http://localhost:8000

## API 엔드포인트

주요 API 엔드포인트 목록입니다. 자세한 내용은 [API 문서](./docs/API.md)를 참고하세요.

### 채팅/정보 탐색 API
- \`POST /api/chat/ask/\` - 질문 및 답변 처리
- \`POST /api/chat/explore/\` 또는 \`GET /api/explore/\` - 정보 탐색 (뉴스 + AI)
- \`GET /api/chat/news/\` - 네이버 뉴스 API 프록시

### 학습 API
- \`GET /api/learn/{mode}/\` - 학습 데이터 조회 (chars, words, sentences, keywords)
- \`POST /api/learn/passage-analyze/\` - 지문 분석
- \`POST /api/learn/extract-keywords/\` - 핵심 키워드 추출
- \`POST /api/learn/extract-key/\` - 핵심 문장 추출

### 점자 API
- \`POST /api/braille/convert/\` - 텍스트 → 점자 변환
- \`POST /api/braille/pattern/\` - 점자 패턴 생성
- \`POST /api/braille/formula/\` - 수식 점자 변환

### 복습 API
- \`GET /api/learning/list/\` - 복습 목록 조회
- \`POST /api/learning/save/\` - 복습 항목 저장
- \`POST /api/learning/enqueue/\` - 복습 큐 추가

### 시험/교재 API (Jeomgeuli-Suneung)
- \`GET /api/exam/textbook/\` - 교재 목록 조회
- \`POST /api/exam/textbook/upload-pdf/\` - PDF 교재 업로드
- \`GET /api/exam/unit/{id}/\` - 단원 상세 조회
- \`GET /api/exam/question/{id}/\` - 문제 상세 조회
- \`POST /api/exam/submit/\` - 답안 제출

### 어휘 API
- \`GET /api/vocab/today/\` - 오늘의 어휘 조회

### 기타 API
- \`GET /api/health/\` - 서버 상태 확인

## 사용법

### 1. 홈 화면
- **점자학습**: 체계적인 점자 학습 과정
- **정보탐색**: AI 기반 정보 접근

### 2. 정보탐색
- 음성이나 텍스트로 질문 입력
- 뉴스 요약, 쉬운 설명, 질문답변 모드 자동 인식
- 핵심 키워드 추출 및 점자 출력

### 3. 점자학습
- 자모 → 단어 → 문장 → 자유변환 순서로 학습
- 각 단계별 TTS 안내 및 자동 테스트
- 오답은 자동으로 복습 노트에 저장

### 4. 복습 노트
- 오답 문제들을 체계적으로 복습
- 음성 안내 및 점자 출력 지원

## 접근성 기능

- **키보드 네비게이션**: Tab/Enter 키로 모든 기능 접근 가능
- **음성 안내**: 모든 주요 기능에 TTS 지원
- **큰 폰트**: 시각적 접근성 향상
- **고대비 모드**: 시각 장애인을 위한 색상 대비 강화
- **점자 출력**: 하드웨어 연동을 통한 점자 디스플레이

## 개발 정보

### 프로젝트 구조
\`\`\`
jeomgeuli/
├── backend/                 # Django 백엔드
│   ├── apps/               # Django 앱들
│   │   ├── chat/          # 채팅/AI 앱
│   │   ├── learn/         # 학습 데이터 앱
│   │   ├── learning/      # 학습 관리/복습 앱
│   │   ├── braille/       # 점자 변환 앱
│   │   ├── exam/          # 시험/교재 앱 (Jeomgeuli-Suneung)
│   │   ├── vocab/         # 어휘 앱
│   │   ├── explore/        # 정보 탐색 앱
│   │   ├── analytics/      # 분석 앱
│   │   ├── newsfeed/       # 뉴스 피드 앱
│   │   └── search/         # 검색 앱
│   ├── jeomgeuli_backend/ # Django 설정
│   ├── utils/              # 공통 유틸리티
│   ├── data/               # 정적 데이터 (JSON)
│   └── requirements.txt
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── hooks/         # 커스텀 훅
│   │   ├── services/      # 서비스 레이어
│   │   ├── lib/           # 라이브러리 (API, 유틸)
│   │   ├── store/         # 상태 관리 (Zustand)
│   │   └── types/         # TypeScript 타입
│   └── package.json
├── docs/                   # 문서
└── README.md
\`\`\`

자세한 구조는 [프로젝트 구조 문서](./PROJECT_STRUCTURE.md)를 참고하세요.

### 환경 변수
\`\`\`env
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # 선택사항
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,8000

# Frontend (.env)
VITE_API_URL=http://localhost:8000/api
\`\`\`

**참고**: Gemini API Key는 필수이며, OpenAI API Key는 선택사항입니다. OpenAI를 사용하지 않으면 Gemini만 사용합니다.

## 라이선스

MIT License

## 기여하기

1. Fork the repository
2. Create your feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add some amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.
# jeomgeuli
# jeomgeuli
# jeomgeuli
# jeomgeuli_v2
# jeomgeuli_v2
