import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import LearnIndex from "../pages/LearnIndex";
import LearnStep from "../pages/LearnStep";
import FreeConvert from "../pages/FreeConvert";
import Quiz from "../pages/Quiz";
import Review from "../pages/Review";
import Explore from "../pages/Explore";
import NotFound from "../pages/NotFound";
import TextbookConverter from "../pages/exam/TextbookConverter";
import TextCompress from "../pages/exam/TextCompress";
import SentenceRepeat from "../pages/exam/SentenceRepeat";
import DevHealth from "../components/system/DevHealth";
import ErrorBoundary from "../components/system/ErrorBoundary";
import HealthCheck from "../components/system/HealthCheck";
import GlobalVoiceRecognition from "../components/input/GlobalVoiceRecognition";
import PerformanceMonitor from "../components/system/PerformanceMonitor";
import VoiceRecognitionDebug from "../components/debug/VoiceRecognitionDebug";
import { useEffect, useRef } from "react";

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
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/explore" element={<Explore />} />

            <Route path="/learn" element={<LearnIndex />} />
            <Route path="/learn/char" element={<LearnStep />} />
            <Route path="/learn/word" element={<LearnStep />} />
            <Route path="/learn/sentence" element={<LearnStep />} />
            <Route path="/learn/free" element={<FreeConvert />} />
            <Route path="/free-convert" element={<FreeConvert />} />

            {/* 퀴즈는 두 경로 모두 수용 */}
            <Route path="/quiz" element={<Quiz />} />
            <Route path="/learn/quiz" element={<Quiz />} />

            <Route path="/review" element={<Review />} />

            {/* 수능 과목 학습 모드 */}
            <Route path="/exam/textbook" element={<TextbookConverter />} />
            <Route path="/exam/compress" element={<TextCompress />} />
            <Route path="/exam/repeat" element={<SentenceRepeat />} />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </HealthCheck>
    </ErrorBoundary>
  );
}