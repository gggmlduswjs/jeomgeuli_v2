import { useCallback } from "react";
import { route } from "../lib/voice/CommandRouter";

type CommandHandlers = {
  // 기본 제어
	next?: () => void;
	prev?: () => void;
	repeat?: () => void;
	pause?: () => void;
	start?: () => void;
	stop?: () => void;
  
  // 네비게이션
	home?: () => void;
	back?: () => void;
	menu?: () => void;
  
  // 학습 관련 (레거시)
	learn?: () => void;
	quiz?: () => void;
	review?: () => void;
	freeConvert?: () => void;
  
  // 정보탐색
	explore?: () => void;
	news?: () => void;
	weather?: () => void;
  
  // 새로운 Jeomgeuli-Suneung 메뉴
	textbook?: () => void;
	passage?: () => void;
	graphTable?: () => void;
	question?: () => void;
	vocab?: () => void;
	brailleSpeed?: () => void;
	examMode?: () => void;
	examTimer?: () => void;
  
  // 점자 관련
	brailleOn?: () => void;
	brailleOff?: () => void;
	brailleConnect?: () => void;
	brailleDisconnect?: () => void;
  
  // 상세 정보
	detail?: (idx?: number) => void;
	help?: () => void;
  
  // TTS 관련
	speak?: (text: string) => void;
	mute?: () => void;
	unmute?: () => void;
  
  // 입력 관련
	clear?: () => void;
	submit?: () => void;
};

/** 한글 서수/기수 매핑 (0-based index 반환) */
const KOREAN_ORDINAL_MAP: Record<string, number> = {
  "첫": 0, "첫째": 0, "첫번째": 0,
  "둘": 1, "두": 1, "둘째": 1, "두번째": 1,
  "셋": 2, "세": 2, "셋째": 2, "세번째": 2,
  "넷": 3, "네": 3, "넷째": 3, "네번째": 3,
  "다섯": 4, "다섯째": 4, "다섯번째": 4,
  "여섯": 5, "여섯째": 5, "여섯번째": 5,
  "일곱": 6, "일곱째": 6, "일곱번째": 6,
  "여덟": 7, "여덟째": 7, "여덟번째": 7,
  "아홉": 8, "아홉째": 8, "아홉번째": 8,
  "열": 9, "열째": 9, "열번째": 9,
};

/** 숫자 표현 → 0-based index */
function extractIndex(t: string): number | undefined {
  // 1) 한글 서수/기수
  for (const k of Object.keys(KOREAN_ORDINAL_MAP)) {
    if (t.includes(k)) return KOREAN_ORDINAL_MAP[k];
  }
  // 2) 숫자 + (번|번째)
  const m1 = t.match(/(\d+)\s*(번|번째)/);
  if (m1) {
    const n = parseInt(m1[1], 10);
    if (!Number.isNaN(n) && n > 0) return n - 1; // 0-based
  }
  // 3) 단독 숫자 (맥락상 detail일 때 자주 말함)
  const m2 = t.match(/\b(\d{1,2})\b/);
  if (m2) {
    const n = parseInt(m2[1], 10);
    if (!Number.isNaN(n) && n > 0) return n - 1;
  }
  return undefined;
}

/** 입력 전처리: 소문자, 공백 정규화, 기호 제거 + 오인식 보정 */
function normalize(raw: string): string {
  let t = String(raw ?? "")
    .toLowerCase()
    .replace(/[~!@#$%^&*()_+=[\]{};:"/\\|<>""''，､、。．·ㆍ…]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  
  // 흔한 오인식 교정 (발음 유사도 고려 - 더 많은 패턴 추가)
  // 학습 메뉴 항목
  t = t.replace(/암호/gi, "단어"); // "암호"는 "단어"로 먼저 처리 (순서 중요!)
  t = t.replace(/잠오|사모|자무|참호|참오/gi, "자모");
  t = t.replace(/다워|다오/gi, "단어");
  t = t.replace(/\bword\b/gi, "단어"); // 영어로 인식된 경우도 보정
  t = t.replace(/문장학습|문장 학습|문창/gi, "문장");
  t = t.replace(/자유변화|편환|편원|편안/gi, "자유변환");
  
  // 페이지 이동 명령
  t = t.replace(/학습모드|학습 모드/gi, "학습");
  t = t.replace(/자유변환|자유 변환|변환모드|변환 모드/gi, "자유변환");
  t = t.replace(/정보탐색|정보 탐색/gi, "탐색");
  
  // 네비게이션 명령
  t = t.replace(/뒤로가|뒤로 가/gi, "뒤로");
  t = t.replace(/이전으로가|이전으로 가/gi, "이전");
  t = t.replace(/홈으로가|홈으로 가|메인으로|메인으로 가/gi, "홈");
  
  // 재생 제어 명령 - '다음' 관련 오인식 보정 (가장 먼저 처리)
  t = t.replace(/\b다움\b/gi, "다음");
  t = t.replace(/\b다응\b/gi, "다음");
  t = t.replace(/\b나음\b/gi, "다음");
  t = t.replace(/\b담\b/gi, "다음");
  t = t.replace(/\b당\b/gi, "다음");
  t = t.replace(/다음으로가|다음으로 가|다음으로가기|다음으로 가기/gi, "다음");
  t = t.replace(/다음으로해|다음으로 해|다음으로넘어가|다음으로 넘어가/gi, "다음");
  t = t.replace(/다음으로넘겨|다음으로 넘겨|다음으로 넘겨줘/gi, "다음");
  t = t.replace(/다음해|다음 해|다음꺼|다음 것|다음거/gi, "다음");
  t = t.replace(/다음꺼로|다음것으로|다음거로/gi, "다음");
  t = t.replace(/이전으로가|이전으로 가/gi, "이전");
  t = t.replace(/다시말해|다시 말해/gi, "다시");
  t = t.replace(/다시읽어|다시 읽어/gi, "다시");
  
  // 입력 제어 명령
  t = t.replace(/다시입력|다시 입력/gi, "지워");
  t = t.replace(/초기화해|초기화 해/gi, "초기화");
  
  // TTS 제어 명령
  t = t.replace(/음성꺼|음성 꺼/gi, "음성 꺼");
  t = t.replace(/음성켜|음성 켜/gi, "음성 켜");
  t = t.replace(/음성멈춰|음성 멈춰/gi, "음성 멈춰");
  
  // 점자 제어 명령
  t = t.replace(/점자켜|점자 켜/gi, "점자 켜");
  t = t.replace(/점자꺼|점자 꺼/gi, "점자 꺼");
  t = t.replace(/점자연결|점자 연결/gi, "점자 연결");
  t = t.replace(/점자해제|점자 해제/gi, "점자 해제");
  
  return t;
}

/** 오인식 패턴 매핑 (대폭 확장 - 발음 유사도 고려) */
const MISRECOGNITION_MAP: Record<string, string> = {
  // 자모 관련 (발음 유사도 고려)
  "자무": "자모", "자모": "자모", "자모.": "자모", "자모 ": "자모",
  "참호": "자모", "참오": "자모", "자모모": "자모", "자모학습": "자모",
  "자모 학습": "자모", "자모로": "자모", "자모를": "자모", "자모에": "자모",
  "자음": "자모", "모음": "자모", "자음모음": "자모", "자음 모음": "자모",
  "자": "자모", "자로": "자모", "자에": "자모",
  
  // 단어 관련
  "단어": "단어", "단어.": "단어", "단어 ": "단어", "다워": "단어",
  "다워.": "단어", "단어로": "단어", "단어를": "단어", "단어에": "단어",
  "단": "단어", "단으로": "단어",
  
  // 문장 관련
  "문장": "문장", "문장.": "문장", "문장 ": "문장", "문장학습": "문장",
  "문장 학습": "문장", "문장으로": "문장", "문장을": "문장", "문장에": "문장",
  "문": "문장", "문으로": "문장",
  
  // 학습 관련
  "학습": "학습", "학습모드": "학습", "학습모드.": "학습", "학습 모드": "학습",
  "학습.": "학습", "학습 ": "학습", "학습하기": "학습", "학습으로": "학습",
  "공부": "학습", "공부하기": "학습", "공부하": "학습", "점자학습": "학습",
  "점자 학습": "학습", "학": "학습",
  
  // 복습 관련
  "복습": "복습", "복습.": "복습", "복습 ": "복습", "복습하기": "복습",
  "복습으로": "복습", "리뷰": "복습", "리뷰하기": "복습", "다시보기": "복습",
  "다시 보기": "복습", "복": "복습",
  
  // 자유변환 관련 (오인식 패턴 포함)
  "자유변환": "자유변환", "자유변환.": "자유변환", "자유 변환": "자유변환",
  "자유변환 ": "자유변환", "자유변환으로": "자유변환", "변환": "자유변환",
  "변환하기": "자유변환", "점자변환": "자유변환", "점자 변환": "자유변환",
  "편환": "자유변환", "편원": "자유변환", "편안": "자유변환", // 오인식 패턴
  "변환모드": "자유변환", "변환 모드": "자유변환",
  
  // 탐색 관련
  "탐색": "탐색", "탐색.": "탐색", "탐색 ": "탐색", "정보탐색": "탐색",
  "정보 탐색": "탐색", "정보": "탐색", "검색": "탐색", "검색하기": "탐색",
  "탐": "탐색",
  
  // 퀴즈 관련
  "퀴즈": "퀴즈", "퀴즈.": "퀴즈", "문제": "퀴즈", "문제풀기": "퀴즈",
  "테스트": "퀴즈", "시험": "퀴즈", "퀴": "퀴즈",
  
  // 홈 관련
  "홈": "홈", "홈으로": "홈", "메인": "홈", "처음으로": "홈", "홈으로가기": "홈",
  
  // 뒤로 관련
  "뒤로": "뒤로", "뒤로가기": "뒤로", "이전": "뒤로", "이전으로": "뒤로",
  "돌아가기": "뒤로", "뒤": "뒤로",
  
  // 다음 관련 (오인식 패턴 포함)
  "다음": "다음", "다음.": "다음", "다음 ": "다음",
  "다움": "다음", "다응": "다음", "나음": "다음", "담": "다음", "당": "다음",
  "다음으로": "다음", "다음으로가": "다음", "다음으로 가": "다음",
  "다음으로해": "다음", "다음으로 해": "다음", "다음으로가기": "다음",
  "다음으로 가기": "다음", "다음으로넘어가": "다음", "다음으로 넘어가": "다음",
  "다음으로넘겨": "다음", "다음으로 넘겨": "다음", "다음으로 넘겨줘": "다음",
  "다음해": "다음", "다음 해": "다음", "다음꺼": "다음", "다음 것": "다음",
  "다음거": "다음", "다음꺼로": "다음", "다음것으로": "다음", "다음거로": "다음",
};

/** 오인식 패턴 보정 (더 관대한 매칭) */
function correctMisrecognition(text: string): string {
  let corrected = text;
  
  // 직접 매핑 확인
  if (MISRECOGNITION_MAP[corrected]) {
    return MISRECOGNITION_MAP[corrected];
  }
  
  // 부분 매칭 (텍스트에 오인식 패턴이 포함된 경우)
  for (const [wrong, correct] of Object.entries(MISRECOGNITION_MAP)) {
    if (corrected.includes(wrong)) {
      corrected = corrected.replace(wrong, correct);
    }
  }
  
  return corrected;
}

/** 명령어 목록 정의 (오인식 패턴 포함) - 모든 명령어에 다양한 표현 추가 */
const COMMAND_PHRASES: Record<string, string[]> = {
  // 페이지 이동 (레거시)
  learn: ["학습", "학습하기", "공부", "점자 학습", "점자학습", "학습모드", "학습 모드", "학", "학습해", "공부해", "학습모드로"],
  quiz: ["퀴즈", "문제", "테스트", "시험", "퀴", "퀴즈해", "문제해", "테스트해"],
  review: ["복습", "리뷰", "다시보기", "다시 보기", "복", "복습해", "리뷰해", "복습모드"],
  freeConvert: ["자유변환", "자유 변환", "변환", "점자변환", "점자 변환", "변환해", "자유변환해", "자유 변환해", "편환", "편원", "편안", "변환모드", "변환 모드"],
  explore: ["탐색", "검색", "정보", "정보탐색", "정보 탐색", "탐", "탐색해", "검색해", "정보해", "탐색모드"],
  textbookConvert: ["교재변환", "교재 변환", "교재", "PDF변환", "PDF 변환", "교재변환해", "교재 변환해", "교재해", "PDF변환해"],
  compress: ["텍스트압축", "텍스트 압축", "압축", "지문압축", "지문 압축", "압축해", "텍스트압축해", "지문압축해"],
  repeat: ["문장반복", "문장 반복", "반복", "문장", "문장반복해", "문장 반복해"],
  
  // 새로운 Jeomgeuli-Suneung 메뉴
  textbook: ["수능특강", "수능특강 학습", "특강", "교재", "수능특강해", "특강해", "교재해"],
  passage: ["국어 지문", "지문 연습", "지문", "국어", "지문 연습해", "지문해", "국어해"],
  graphTable: ["그래프 도표", "그래프", "도표", "그래프 해석", "도표 해석", "그래프도표", "그래프해석", "도표해석"],
  question: ["문항 풀이", "문항", "문제 풀이", "오답노트", "문항해", "문제해", "오답"],
  vocab: ["어휘 시사", "어휘", "시사", "어휘 학습", "시사 학습", "어휘시사", "어휘해", "시사해"],
  brailleSpeed: ["점자 속도", "속도 훈련", "점자 속도 훈련", "속도", "점자속도", "속도훈련"],
  examMode: ["실전 모의고사", "모의고사", "실전", "모의고사해", "실전해"],
  examTimer: ["시험시간", "시간 관리", "시험시간 관리", "타이머", "시험시간해", "타이머해"],
  
  home: ["홈", "메인", "처음으로", "홈으로", "홈으로가", "메인으로", "집"],
  back: ["뒤로", "이전", "뒤로가기", "이전으로", "돌아가기", "뒤", "뒤로가", "이전으로가"],
  menu: ["메뉴", "목록", "메뉴보기", "목록보기"],
  
  // 긴급 제어
  stop: ["멈춰", "정지", "스탑", "일시정지", "일시 정지", "중지", "멈", "멈춰줘", "정지해", "스탑해"],
  pause: ["일시정지", "일시 정지", "잠시멈춤", "잠시 멈춤", "멈춤"],
  
  // 재생 제어
  next: [
    "다음", "넘겨", "다음으로", "계속", "진행", 
    "다음해", "넘겨줘", "계속해", "진행해",
    "다음으로가", "다음으로 가", "다음으로해", "다음으로 해",
    "다음으로가기", "다음으로 가기", "다음으로넘어가", "다음으로 넘어가",
    "다음으로넘겨", "다음으로 넘겨", "다음으로 넘겨줘",
    "다음꺼", "다음 것", "다음거", "다음꺼로", "다음것으로", "다음거로",
    "다움", "다응", "나음", "담", "당"  // 오인식 패턴도 포함
  ],
  prev: ["이전", "이전으로", "뒤로", "이전해", "이전으로가"],
  repeat: ["반복", "다시", "다시 말해", "다시 읽어", "재생", "반복해", "다시해", "재생해"],
  start: ["시작", "시작해", "재개", "계속해", "시작하기", "재개해"],
  
  // 입력 제어
  clear: ["지워", "삭제", "초기화", "다시 입력", "지워줘", "삭제해", "초기화해", "다시입력해"],
  submit: ["전송", "제출", "확인", "입력", "전송해", "제출해", "확인해", "입력해"],
  
  // TTS 제어
  mute: ["음성 꺼", "음성 중지", "음성 멈춰", "음성 비활성화", "음성꺼", "음성중지", "음성멈춰"],
  unmute: ["음성 켜", "음성 활성화", "음성 시작", "음성켜", "음성활성화", "음성시작"],
  
  // 상세 정보
  detail: ["자세히", "더 알려줘", "자세하게", "상세히", "자세히해", "더알려줘"],
  help: ["도움말", "도움", "헬프", "사용법", "명령어", "도움말해", "도움해"],
  
  // 정보 서비스
  news: ["뉴스", "뉴스 보기", "오늘 뉴스", "뉴스보기", "오늘뉴스"],
  weather: ["날씨", "날씨 보기", "오늘 날씨", "날씨보기", "오늘날씨"],
  
  // 점자 제어
  brailleOn: ["점자 출력 켜", "점자 켜", "점자 시작", "점자 활성화", "점자출력켜", "점자켜", "점자시작", "점자활성화"],
  brailleOff: ["점자 출력 꺼", "점자 꺼", "점자 중지", "점자 비활성화", "점자출력꺼", "점자꺼", "점자중지", "점자비활성화"],
  brailleConnect: ["점자 연결", "점자 디스플레이 연결", "블루투스 연결", "점자연결", "점자디스플레이연결", "블루투스연결"],
  brailleDisconnect: ["점자 해제", "점자 디스플레이 해제", "블루투스 해제", "점자해제", "점자디스플레이해제", "블루투스해제"],
  
  // 학습 메뉴 항목 (오인식 패턴 포함)
  jamo: ["자모", "자음", "모음", "자음모음", "자음 모음", "자무", "자", "잠오", "사모", "참호", "참오"],
  word: ["단어", "워드", "다워", "단", "다오", "암호"], // "암호"도 "단어"로 인식
  sentence: ["문장", "센턴스", "문"],
};

/** 퍼지 매칭으로 명령 찾기 (string-similarity 사용) */
function matchCommand(text: string, threshold: number = 0.40): string | undefined {
  const t = normalize(text);
  let bestCmd: string | undefined;
  let bestScore = 0;
  
  for (const [cmd, phrases] of Object.entries(COMMAND_PHRASES)) {
    for (const phrase of phrases) {
      const score = compareTwoStrings(t, phrase);
      if (score > bestScore) {
        bestScore = score;
        bestCmd = cmd;
      }
    }
  }
  
  // "다음" 명령어는 더 관대한 임계값 적용 (0.30으로 낮춤)
  const finalThreshold = bestCmd === 'next' ? Math.min(threshold, 0.30) : threshold;
  
  // 임계값 이상이면 명령 반환
  if (bestScore >= finalThreshold) {
    console.log(`[VoiceCommands] 퍼지 매칭: "${text}" -> "${bestCmd}" (유사도: ${(bestScore * 100).toFixed(1)}%, 임계값: ${(finalThreshold * 100).toFixed(1)}%)`);
    return bestCmd;
  }
  
  return undefined;
}

// Thresholds via env (lenient for navigation/mode; stricter for destructive)
const NAV_THRESHOLD = Number((import.meta as any).env?.VITE_VOICE_FUZZY_THRESHOLD_NAV ?? 0.35);
const DESTRUCT_THRESHOLD = Number((import.meta as any).env?.VITE_VOICE_FUZZY_THRESHOLD_DESTRUCT ?? 0.40);
const DESTRUCTIVE_SET = new Set<string>(['mute', 'clear', 'submit', 'stop', 'brailleOff']);

// 명령 쿨다운 (연타 방지)
const cmdCoolUntil: Record<string, number> = {};
function canRun(name: string, ms: number): boolean {
  const now = Date.now();
  if ((cmdCoolUntil[name] ?? 0) > now) return false;
  cmdCoolUntil[name] = now + ms;
  return true;
}

/** 키워드 기반 유연한 매칭 (핵심 단어만 있어도 인식) */
function fuzzyMatch(text: string, keywords: string[]): boolean {
  const normalized = text.toLowerCase();
  
  // 완전 일치
  for (const keyword of keywords) {
    if (normalized === keyword.toLowerCase()) return true;
    if (normalized.includes(keyword.toLowerCase())) return true;
  }
  
  // 첫 글자 매칭 (2-3글자 단어의 경우)
  for (const keyword of keywords) {
    if (keyword.length <= 3 && normalized.startsWith(keyword[0])) {
      return true;
    }
  }
  
  // 부분 문자열 매칭 (핵심 글자 포함)
  for (const keyword of keywords) {
    if (keyword.length >= 2) {
      const firstTwo = keyword.substring(0, 2).toLowerCase();
      if (normalized.includes(firstTwo)) return true;
    }
  }
  
  return false;
}

/** 간단한 유사도 계산 (Levenshtein 거리 기반) */
function similarity(s1: string, s2: string): number {
  const longer = s1.length > s2.length ? s1 : s2;
  const shorter = s1.length > s2.length ? s2 : s1;
  
  if (longer.length === 0) return 1.0;
  
  // 완전 일치
  if (s1 === s2) return 1.0;
  
  // 부분 일치 (한 단어가 다른 단어에 포함)
  if (longer.includes(shorter)) return 0.8;
  if (shorter.includes(longer)) return 0.8;
  
  // 첫 글자 일치
  if (s1[0] === s2[0] && s1.length <= 3 && s2.length <= 3) return 0.6;
  
  // 간단한 편집 거리 (최대 1글자 차이)
  if (Math.abs(s1.length - s2.length) <= 1) {
    let diff = 0;
    const minLen = Math.min(s1.length, s2.length);
    for (let i = 0; i < minLen; i++) {
      if (s1[i] !== s2[i]) diff++;
    }
    if (diff <= 1) return 0.7;
  }
  
  return 0;
}

export default function useVoiceCommands(handlers: CommandHandlers) {
  const onSpeech = useCallback((text: string): boolean => route(text, handlers), [handlers]);
  return { onSpeech };
}
