import { BrowserRouter, Routes, Route } from "react-router-dom";
import { lazy, Suspense, useEffect, useRef } from "react";
import ErrorBoundary from "../components/system/ErrorBoundary";
import GlobalVoiceRecognition from "../components/input/GlobalVoiceRecognition";
import PerformanceMonitor from "../components/system/PerformanceMonitor";
import DevHealth from "../components/system/DevHealth";
import HealthCheck from "../components/system/HealthCheck";
import VoiceRecognitionDebug from "../components/debug/VoiceRecognitionDebug";

// Lazy load pages for code splitting
const Home = lazy(() => import("../pages/Home"));
const LearnIndex = lazy(() => import("../pages/LearnIndex"));
const LearnStep = lazy(() => import("../pages/LearnStep"));
const FreeConvert = lazy(() => import("../pages/FreeConvert"));
const Quiz = lazy(() => import("../pages/Quiz"));
const Review = lazy(() => import("../pages/Review"));
const Explore = lazy(() => import("../pages/Explore"));
const NotFound = lazy(() => import("../pages/NotFound"));
const TextbookConverter = lazy(() => import("../pages/exam/TextbookConverter"));
const TextCompress = lazy(() => import("../pages/exam/TextCompress"));
const SentenceRepeat = lazy(() => import("../pages/exam/SentenceRepeat"));
// New Jeomgeuli-Suneung pages
const Textbook = lazy(() => import("../pages/Textbook/Textbook"));
const Passage = lazy(() => import("../pages/Passage/Passage"));
const GraphTable = lazy(() => import("../pages/GraphTable/GraphTable"));
const Question = lazy(() => import("../pages/Question/Question"));
const Vocab = lazy(() => import("../pages/Vocab/Vocab"));
const BrailleSpeed = lazy(() => import("../pages/BrailleSpeed/BrailleSpeed"));
const ExamMode = lazy(() => import("../pages/ExamMode/ExamMode"));
const ExamTimer = lazy(() => import("../pages/ExamTimer/ExamTimer"));

// Loading component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen" role="status" aria-label="페이지 로딩 중">
    <div className="text-lg">로딩 중...</div>
  </div>
);

export default function App(){
  // 개발 헬스 기록
  (window as any).__APP_HEALTH__ = { ...(window as any).__APP_HEALTH__, appMounted: true };
  console.log("[APP] mounted", (window as any).__APP_HEALTH__);

  // 전역 마이크 모드 시 모든 미디어 볼륨/재생 제어 (추가 음소거)
  const pausedMediaRef = useRef<HTMLMediaElement[]>([]);
  const volumeMapRef = useRef<Map<HTMLMediaElement, number>>(new Map());
  useEffect(() => {
    const onMicMode = (e: Event) => {
      const active = !!(e as CustomEvent)?.detail?.active;
      try {
        const media = Array.from(document.querySelectorAll('audio,video')) as HTMLMediaElement[];
        if (active) {
          pausedMediaRef.current = [];
          volumeMapRef.current.clear();
          media.forEach(m => {
            // 저장 후 즉시 음소거 및 일시정지
            if (!volumeMapRef.current.has(m)) volumeMapRef.current.set(m, m.volume);
            m.volume = 0;
            if (!m.paused && !m.ended) {
              try { m.pause(); pausedMediaRef.current.push(m); } catch {}
            }
          });
        } else {
          // 복귀: 볼륨 복원(일단 0→원래값), 필요 시 재생 복귀는 스킵
          media.forEach(m => {
            const prev = volumeMapRef.current.get(m);
            if (typeof prev === 'number') {
              m.volume = prev;
            }
          });
          volumeMapRef.current.clear();
          pausedMediaRef.current = [];
        }
      } catch {}
    };
    window.addEventListener('voice:mic-mode', onMicMode as EventListener);
    return () => window.removeEventListener('voice:mic-mode', onMicMode as EventListener);
  }, []);

  return (
    <ErrorBoundary>
      <HealthCheck>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          {import.meta.env.DEV && <DevHealth />}
          {import.meta.env.DEV && <PerformanceMonitor />}
          {import.meta.env.DEV && <VoiceRecognitionDebug />}
          {/* 전역 음성 인식: 모든 페이지에서 화면을 길게 누르면 음성 인식 시작 */}
          <GlobalVoiceRecognition />
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Home />} />
              
              {/* New Jeomgeuli-Suneung routes */}
              <Route path="/textbook" element={<Textbook />} />
              <Route path="/passage" element={<Passage />} />
              <Route path="/graph-table" element={<GraphTable />} />
              <Route path="/question" element={<Question />} />
              <Route path="/vocab" element={<Vocab />} />
              <Route path="/braille-speed" element={<BrailleSpeed />} />
              <Route path="/exam-mode" element={<ExamMode />} />
              <Route path="/exam-timer" element={<ExamTimer />} />

              {/* Legacy routes (backward compatibility) */}
              <Route path="/explore" element={<Explore />} />
              <Route path="/learn" element={<LearnIndex />} />
              <Route path="/learn/char" element={<LearnStep />} />
              <Route path="/learn/word" element={<LearnStep />} />
              <Route path="/learn/sentence" element={<LearnStep />} />
              <Route path="/learn/free" element={<FreeConvert />} />
              <Route path="/free-convert" element={<FreeConvert />} />
              <Route path="/quiz" element={<Quiz />} />
              <Route path="/learn/quiz" element={<Quiz />} />
              <Route path="/review" element={<Review />} />
              <Route path="/exam/textbook" element={<TextbookConverter />} />
              <Route path="/exam/compress" element={<TextCompress />} />
              <Route path="/exam/repeat" element={<SentenceRepeat />} />

              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </HealthCheck>
    </ErrorBoundary>
  );
}