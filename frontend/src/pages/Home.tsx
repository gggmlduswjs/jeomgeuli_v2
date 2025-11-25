import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Search, RotateCcw, Type, FileText, Minimize2, Repeat } from 'lucide-react';
import AppShellMobile from '../components/ui/AppShellMobile';
import SpeechBar from '../components/input/SpeechBar';
import useTTS from '../hooks/useTTS';
import useSTT from '../hooks/useSTT';
import useVoiceCommands from '../hooks/useVoiceCommands';
import micMode from '../lib/voice/MicMode';
import ToastA11y from '../components/system/ToastA11y';

export default function Home() {
  const navigate = useNavigate();
  const { speak, stop: stopTTS } = useTTS();
  const { start: startSTT, stop: stopSTT, isListening, transcript } = useSTT();
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  // 페이지 진입 시 자동 음성 안내
  useEffect(() => {
    const onboardingMessage =
      '시각장애인 수능 학습 앱, 점글이입니다. 메인화면에 점자기초, 교재변환, 텍스트압축, 문장반복, 복습하기 모드가 있습니다. 모드를 선택해주세요.';

    // 페이지 진입 시 즉시 안내 음성 재생
    const timer = setTimeout(() => {
      speak(onboardingMessage);
    }, 500); // 0.5초 후 재생 (페이지 로딩 완료 후)

    return () => {
      clearTimeout(timer);
    };
  }, [speak]);

  // 음성 명령어 시스템
  const { onSpeech } = useVoiceCommands({
    // 네비게이션
    home: () => {
      showToastMessage('이미 홈 화면입니다.');
      speak('이미 홈 화면입니다.');
    },
    back: () => {
      showToastMessage('홈 화면에서는 뒤로 갈 수 없습니다.');
      speak('홈 화면에서는 뒤로 갈 수 없습니다.');
    },
    
    // 페이지 이동
    learn: () => {
      stopTTS(); // 기존 TTS 중지
      navigate('/learn');
      showToastMessage('점자 학습 모드로 이동합니다.');
      speak('점자 학습 모드로 이동합니다.');
      stopSTT();
    },
    explore: () => {
      stopTTS(); // 기존 TTS 중지
      navigate('/explore');
      showToastMessage('정보 탐색 모드로 이동합니다.');
      speak('정보 탐색 모드로 이동합니다.');
      stopSTT();
    },
    review: () => {
      stopTTS(); // 기존 TTS 중지
      navigate('/review');
      showToastMessage('복습 모드로 이동합니다.');
      speak('복습 모드로 이동합니다.');
      stopSTT();
    },
    freeConvert: () => {
      stopTTS(); // 기존 TTS 중지
      navigate('/free-convert');
      showToastMessage('자유 변환 모드로 이동합니다.');
      speak('자유 변환 모드로 이동합니다.');
      stopSTT();
    },
    textbookConvert: () => {
      stopTTS();
      navigate('/exam/textbook');
      showToastMessage('교재 변환 모드로 이동합니다.');
      speak('교재 변환 모드로 이동합니다.');
      stopSTT();
    },
    compress: () => {
      stopTTS();
      navigate('/exam/compress');
      showToastMessage('텍스트 압축 모드로 이동합니다.');
      speak('텍스트 압축 모드로 이동합니다.');
      stopSTT();
    },
    repeat: () => {
      stopTTS();
      navigate('/exam/repeat');
      showToastMessage('문장 반복 모드로 이동합니다.');
      speak('문장 반복 모드로 이동합니다.');
      stopSTT();
    },
    quiz: () => {
      stopTTS(); // 기존 TTS 중지
      navigate('/quiz');
      showToastMessage('퀴즈 모드로 이동합니다.');
      speak('퀴즈 모드로 이동합니다.');
      stopSTT();
    },
    
    // 도움말
    help: () => {
      stopTTS(); // 기존 TTS 중지
      const helpText = '사용 가능한 음성 명령어: 점자기초, 교재변환, 텍스트압축, 문장반복, 복습, 도움말, 앱소개듣기';
      speak(helpText);
      showToastMessage('도움말을 음성으로 안내합니다.');
    },
    
    // TTS 제어
    speak: (text: string) => {
      stopTTS(); // 기존 TTS 중지
      speak(text);
    },
    mute: () => {
      stopTTS(); // 기존 TTS 중지
      showToastMessage('음성이 비활성화되었습니다.');
    },
    unmute: () => {
      showToastMessage('음성이 활성화되었습니다.');
      speak('음성이 활성화되었습니다.');
    },
  });

  // 음성 명령 처리
  useEffect(() => {
    if (!transcript) return;
    onSpeech(transcript);
  }, [transcript, onSpeech]);

  const showToastMessage = (message: string) => {
    setToastMessage(message);
    setShowToast(true);
  };

  // 각 메뉴로 이동하는 핸들러
  const goLearn = () => {
    stopTTS();
    navigate('/learn');
    showToastMessage('점자 학습 모드로 이동합니다.');
    speak('점자 학습 모드로 이동합니다.');
    stopSTT();
  };
  const goExplore = () => {
    stopTTS();
    navigate('/explore');
    showToastMessage('정보 탐색 모드로 이동합니다.');
    speak('정보 탐색 모드로 이동합니다.');
    stopSTT();
  };
  const goReview = () => {
    stopTTS();
    navigate('/review');
    showToastMessage('복습 모드로 이동합니다.');
    speak('복습 모드로 이동합니다.');
    stopSTT();
  };
  const goFree = () => {
    stopTTS();
    navigate('/free-convert');
    showToastMessage('자유 변환 모드로 이동합니다.');
    speak('자유 변환 모드로 이동합니다.');
    stopSTT();
  };
  const goTextbook = () => {
    stopTTS();
    navigate('/exam/textbook');
    showToastMessage('교재 변환 모드로 이동합니다.');
    speak('교재 변환 모드로 이동합니다.');
    stopSTT();
  };
  const goCompress = () => {
    stopTTS();
    navigate('/exam/compress');
    showToastMessage('텍스트 압축 모드로 이동합니다.');
    speak('텍스트 압축 모드로 이동합니다.');
    stopSTT();
  };
  const goRepeat = () => {
    stopTTS();
    navigate('/exam/repeat');
    showToastMessage('문장 반복 모드로 이동합니다.');
    speak('문장 반복 모드로 이동합니다.');
    stopSTT();
  };

  // 원형 메뉴 버튼 컴포넌트 (임시로 마우스 클릭 가능 - 나중에 제거 예정)
  const RadialButton = ({ 
    label, 
    onClick, 
    Icon, 
    color = "primary",
    command
  }: { 
    label: string; 
    onClick: () => void; 
    Icon: React.ComponentType<{ className?: string }>; 
    color?: "primary" | "success" | "accent" | "sky";
    command?: string;
  }) => {
    const colorClasses = {
      primary: "bg-primary/10 hover:bg-primary/20 text-primary border-primary/20",
      success: "bg-success/10 hover:bg-success/20 text-success border-success/20",
      accent: "bg-accent/10 hover:bg-accent/20 text-accent border-accent/20",
      sky: "bg-sky/10 hover:bg-sky/20 text-sky border-sky/20",
    };

    return (
      <button
        onClick={onClick}
        className={`flex flex-col items-center justify-center w-14 h-14 md:w-16 md:h-16 rounded-full border-2 transition-all duration-300 shadow-lg cursor-pointer hover:scale-105 active:scale-95 touch-manipulation ${colorClasses[color]}`}
        aria-label={command ? `${label} (음성으로 "${command}"라고 말하세요)` : label}
      >
        <Icon className="w-5 h-5 md:w-6 md:h-6 mb-0.5" />
        <span className="text-[10px] md:text-xs font-medium whitespace-nowrap">{label}</span>
      </button>
    );
  };

  return (
    <AppShellMobile title="점글이" className="relative">
      {/* 음성 명령 표시줄 */}
      <div className="mb-4">
        <SpeechBar isListening={isListening} transcript={transcript} />
      </div>

      {/* 원형 메뉴 인터페이스 */}
      <div className="flex justify-center items-center my-6 md:my-8 px-4">
        <div className="relative w-[320px] h-[320px] md:w-[360px] md:h-[360px] rounded-full bg-gradient-to-br from-primary/5 via-accent/5 to-sky/5 border-2 border-primary/20 shadow-2xl flex items-center justify-center backdrop-blur-sm">
          {/* 중앙 로고 버튼: 길게 눌러 음성 인식 시작 */}
          <button
            onPointerDown={(e) => {
              // TTS 중지 및 마이크 시작 (버튼이므로 GlobalVoiceRecognition 필터링에 걸리므로 직접 처리)
              try { stopTTS(); } catch {}
              micMode.requestStart();
            }}
            onPointerUp={(e) => {
              // 마이크 중지
              micMode.requestStop();
            }}
            className={`absolute inset-[33%] rounded-full bg-gradient-to-br from-primary via-primary/90 to-accent text-white flex items-center justify-center focus:outline-none shadow-2xl transition-all duration-300 hover:scale-105 active:scale-95 touch-manipulation ${
              isListening ? 'animate-pulse ring-4 ring-primary/50 ring-offset-2' : 'hover:ring-2 hover:ring-primary/30'
            }`}
            aria-label="음성 인식 시작"
          >
            <div className="flex flex-col items-center justify-center px-3 py-1.5 md:px-4">
              <span 
                className="text-5xl md:text-6xl font-bold mb-1 md:mb-2 leading-none select-none" 
                style={{ fontFamily: 'monospace', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}
                aria-hidden="true"
              >
                ⠿
              </span>
              <span className="text-xs md:text-sm font-semibold opacity-95 tracking-wide">점글이</span>
            </div>
          </button>
          
          {/* 상단 버튼: 점자 기초 */}
          <div className="absolute -top-6 md:-top-8 left-1/2 transform -translate-x-1/2 z-10">
            <RadialButton label="점자기초" Icon={BookOpen} onClick={goLearn} color="primary" command="점자기초" />
          </div>
          {/* 오른쪽 상단 버튼: 교재변환 */}
          <div className="absolute top-[15%] right-[15%] z-10">
            <RadialButton label="교재변환" Icon={FileText} onClick={goTextbook} color="success" command="교재변환" />
          </div>
          {/* 오른쪽 하단 버튼: 텍스트압축 */}
          <div className="absolute bottom-[15%] right-[15%] z-10">
            <RadialButton label="텍스트압축" Icon={Minimize2} onClick={goCompress} color="accent" command="텍스트압축" />
          </div>
          {/* 하단 버튼: 복습 */}
          <div className="absolute -bottom-6 md:-bottom-8 left-1/2 transform -translate-x-1/2 z-10">
            <RadialButton label="복습" Icon={RotateCcw} onClick={goReview} color="accent" command="복습" />
          </div>
          {/* 왼쪽 하단 버튼: 문장반복 */}
          <div className="absolute bottom-[15%] left-[15%] z-10">
            <RadialButton label="문장반복" Icon={Repeat} onClick={goRepeat} color="sky" command="문장반복" />
          </div>
          {/* 왼쪽 상단 버튼: 자유변환 (기존 유지) */}
          <div className="absolute top-[15%] left-[15%] z-10">
            <RadialButton label="자유변환" Icon={Type} onClick={goFree} color="sky" command="자유변환" />
          </div>
        </div>
      </div>

      {/* 안내 메시지 */}
      <div className="mt-6 text-center">
        <p className="text-sm text-muted mb-3">
          중앙 로고를 길게 눌러 음성 명령을 사용하세요
        </p>
        <button
          onClick={() =>
            speak(
              '시각장애인 수능 학습 앱, 점글이입니다. 메인화면에 점자기초, 교재변환, 텍스트압축, 문장반복, 복습하기 모드가 있습니다. 모드를 선택해주세요.'
            )
          }
          className="text-sm text-primary hover:text-primary/80 underline transition-colors"
          aria-label="앱 소개 음성 안내 듣기"
        >
          🔊 앱 소개 듣기
        </button>
      </div>

      {/* 토스트 알림: 항상 마운트 + isVisible 토글 */}
      <ToastA11y
        message={toastMessage}
        isVisible={showToast}
        duration={3000}
        onClose={() => setShowToast(false)}
      />
    </AppShellMobile>
  );
}
