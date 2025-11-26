import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  FileText, 
  BarChart3, 
  HelpCircle, 
  BookMarked, 
  Gauge, 
  Calculator,
  Globe,
  FlaskConical,
  Building2
} from 'lucide-react';
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
      '수능 점자 읽기 훈련 앱입니다. 과목을 선택하세요. 수학 읽기, 국어 읽기, 영어 읽기, 과학 읽기, 사회 읽기, 어휘 읽기, 속도 훈련이 있습니다.';

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
    
    // 과목별 점자 읽기 메뉴 항목
    math: () => {
      stopTTS();
      navigate('/textbook?subject=math&mode=braille-read');
      showToastMessage('수학 점자 읽기 모드로 이동합니다.');
      speak('수학 점자 읽기 모드로 이동합니다.');
      stopSTT();
    },
    korean: () => {
      stopTTS();
      navigate('/textbook?subject=korean&mode=braille-read');
      showToastMessage('국어 점자 읽기 모드로 이동합니다.');
      speak('국어 점자 읽기 모드로 이동합니다.');
      stopSTT();
    },
    english: () => {
      stopTTS();
      navigate('/textbook?subject=english&mode=braille-read');
      showToastMessage('영어 점자 읽기 모드로 이동합니다.');
      speak('영어 점자 읽기 모드로 이동합니다.');
      stopSTT();
    },
    science: () => {
      stopTTS();
      navigate('/textbook?subject=science&mode=braille-read');
      showToastMessage('과학 점자 읽기 모드로 이동합니다.');
      speak('과학 점자 읽기 모드로 이동합니다.');
      stopSTT();
    },
    social: () => {
      stopTTS();
      navigate('/textbook?subject=social&mode=braille-read');
      showToastMessage('사회 점자 읽기 모드로 이동합니다.');
      speak('사회 점자 읽기 모드로 이동합니다.');
      stopSTT();
    },
    vocab: () => {
      stopTTS();
      navigate('/vocab?mode=braille-read');
      showToastMessage('어휘 점자 읽기 모드로 이동합니다.');
      speak('어휘 점자 읽기 모드로 이동합니다.');
      stopSTT();
    },
    brailleSpeed: () => {
      stopTTS();
      navigate('/braille-speed');
      showToastMessage('점자 속도 훈련 모드로 이동합니다.');
      speak('점자 속도 훈련 모드로 이동합니다.');
      stopSTT();
    },
    
    // 레거시 호환 (기존 명령어도 지원)
    learn: () => {
      stopTTS();
      navigate('/textbook');
      showToastMessage('수능특강 학습 모드로 이동합니다.');
      speak('수능특강 학습 모드로 이동합니다.');
      stopSTT();
    },
    explore: () => {
      stopTTS();
      navigate('/vocab');
      showToastMessage('어휘 시사 학습 모드로 이동합니다.');
      speak('어휘 시사 학습 모드로 이동합니다.');
      stopSTT();
    },
    quiz: () => {
      stopTTS();
      navigate('/question');
      showToastMessage('문항 풀이 모드로 이동합니다.');
      speak('문항 풀이 모드로 이동합니다.');
      stopSTT();
    },
    
    // 도움말
    help: () => {
      stopTTS();
      const helpText = '사용 가능한 음성 명령어: 수학 읽기, 국어 읽기, 영어 읽기, 과학 읽기, 사회 읽기, 어휘 읽기, 속도 훈련, 도움말, 앱소개듣기';
      speak(helpText);
      showToastMessage('도움말을 음성으로 안내합니다.');
    },
    
    // TTS 제어
    speak: (text: string) => {
      stopTTS();
      speak(text);
    },
    mute: () => {
      stopTTS();
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

  // 과목별 점자 읽기 메뉴 핸들러
  const goMath = () => {
    stopTTS();
    navigate('/textbook?subject=math&mode=braille-read');
    showToastMessage('수학 점자 읽기 모드로 이동합니다.');
    speak('수학 점자 읽기 모드로 이동합니다.');
    stopSTT();
  };
  const goKorean = () => {
    stopTTS();
    navigate('/textbook?subject=korean&mode=braille-read');
    showToastMessage('국어 점자 읽기 모드로 이동합니다.');
    speak('국어 점자 읽기 모드로 이동합니다.');
    stopSTT();
  };
  const goEnglish = () => {
    stopTTS();
    navigate('/textbook?subject=english&mode=braille-read');
    showToastMessage('영어 점자 읽기 모드로 이동합니다.');
    speak('영어 점자 읽기 모드로 이동합니다.');
    stopSTT();
  };
  const goScience = () => {
    stopTTS();
    navigate('/textbook?subject=science&mode=braille-read');
    showToastMessage('과학 점자 읽기 모드로 이동합니다.');
    speak('과학 점자 읽기 모드로 이동합니다.');
    stopSTT();
  };
  const goSocial = () => {
    stopTTS();
    navigate('/textbook?subject=social&mode=braille-read');
    showToastMessage('사회 점자 읽기 모드로 이동합니다.');
    speak('사회 점자 읽기 모드로 이동합니다.');
    stopSTT();
  };
  const goVocab = () => {
    stopTTS();
    navigate('/vocab?mode=braille-read');
    showToastMessage('어휘 점자 읽기 모드로 이동합니다.');
    speak('어휘 점자 읽기 모드로 이동합니다.');
    stopSTT();
  };
  const goBrailleSpeed = () => {
    stopTTS();
    navigate('/braille-speed');
    showToastMessage('점자 속도 훈련 모드로 이동합니다.');
    speak('점자 속도 훈련 모드로 이동합니다.');
    stopSTT();
  };

  // 원형 메뉴 버튼 컴포넌트
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
    color?: "primary" | "success" | "accent" | "sky" | "purple" | "orange" | "teal" | "pink";
    command?: string;
  }) => {
    const colorClasses = {
      primary: "bg-primary/10 hover:bg-primary/20 text-primary border-primary/20",
      success: "bg-success/10 hover:bg-success/20 text-success border-success/20",
      accent: "bg-accent/10 hover:bg-accent/20 text-accent border-accent/20",
      sky: "bg-sky/10 hover:bg-sky/20 text-sky border-sky/20",
      purple: "bg-purple-500/10 hover:bg-purple-500/20 text-purple-600 border-purple-500/20",
      orange: "bg-orange-500/10 hover:bg-orange-500/20 text-orange-600 border-orange-500/20",
      teal: "bg-teal-500/10 hover:bg-teal-500/20 text-teal-600 border-teal-500/20",
      pink: "bg-pink-500/10 hover:bg-pink-500/20 text-pink-600 border-pink-500/20",
    };

    return (
      <button
        onClick={onClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onClick();
          }
        }}
        className={`flex flex-col items-center justify-center w-14 h-14 md:w-16 md:h-16 rounded-full border-2 transition-all duration-300 shadow-lg cursor-pointer hover:scale-105 active:scale-95 touch-manipulation focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${colorClasses[color]}`}
        aria-label={command ? `${label} (음성으로 "${command}"라고 말하세요)` : label}
        role="button"
        tabIndex={0}
      >
        <Icon className="w-5 h-5 md:w-6 md:h-6 mb-0.5" aria-hidden="true" />
        <span className="text-[10px] md:text-xs font-medium whitespace-nowrap text-center leading-tight">{label}</span>
      </button>
    );
  };

  return (
    <AppShellMobile title="점글이 수능" className="relative">
      {/* 음성 명령 표시줄 */}
      <div className="mb-4">
        <SpeechBar isListening={isListening} transcript={transcript} />
      </div>

      {/* 원형 메뉴 인터페이스 - 8개 메뉴 */}
      <div className="flex justify-center items-center my-6 md:my-8 px-4">
        <nav 
          className="relative w-[400px] h-[400px] md:w-[450px] md:h-[450px] rounded-full bg-gradient-to-br from-primary/5 via-accent/5 to-sky/5 border-2 border-primary/20 shadow-2xl flex items-center justify-center backdrop-blur-sm"
          role="navigation"
          aria-label="메인 메뉴"
        >
          {/* 중앙 로고 버튼: 길게 눌러 음성 인식 시작 */}
          <button
            onPointerDown={(e) => {
              try { stopTTS(); } catch {}
              micMode.requestStart();
            }}
            onPointerUp={(e) => {
              micMode.requestStop();
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                try { stopTTS(); } catch {}
                if (isListening) {
                  micMode.requestStop();
                } else {
                  micMode.requestStart();
                }
              }
            }}
            className={`absolute inset-[35%] rounded-full bg-gradient-to-br from-primary via-primary/90 to-accent text-white flex items-center justify-center focus:outline-none focus:ring-4 focus:ring-primary/50 focus:ring-offset-2 shadow-2xl transition-all duration-300 hover:scale-105 active:scale-95 touch-manipulation ${
              isListening ? 'animate-pulse ring-4 ring-primary/50 ring-offset-2' : 'hover:ring-2 hover:ring-primary/30'
            }`}
            aria-label={isListening ? "음성 인식 중입니다. 다시 누르면 중지됩니다" : "음성 인식 시작 (Enter 또는 Space 키)"}
            aria-pressed={isListening}
            role="button"
            tabIndex={0}
          >
            <div className="flex flex-col items-center justify-center px-3 py-1.5 md:px-4">
              <span 
                className="text-5xl md:text-6xl font-bold mb-1 md:mb-2 leading-none select-none" 
                style={{ fontFamily: 'monospace', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}
                aria-hidden="true"
              >
                ⠿
              </span>
              <span className="text-xs md:text-sm font-semibold opacity-95 tracking-wide">점글이 수능</span>
            </div>
          </button>
          
          {/* 1. 상단: 수학 읽기 */}
          <div className="absolute -top-4 md:-top-6 left-1/2 transform -translate-x-1/2 z-10">
            <RadialButton label="수학 읽기" Icon={Calculator} onClick={goMath} color="primary" command="수학 점자 읽기" />
          </div>
          
          {/* 2. 오른쪽 상단: 국어 읽기 */}
          <div className="absolute top-[12%] right-[12%] z-10">
            <RadialButton label="국어 읽기" Icon={BookOpen} onClick={goKorean} color="success" command="국어 점자 읽기" />
          </div>
          
          {/* 3. 오른쪽: 영어 읽기 */}
          <div className="absolute top-1/2 right-0 transform translate-y-[-50%] z-10">
            <RadialButton label="영어 읽기" Icon={Globe} onClick={goEnglish} color="accent" command="영어 점자 읽기" />
          </div>
          
          {/* 4. 오른쪽 하단: 과학 읽기 */}
          <div className="absolute bottom-[12%] right-[12%] z-10">
            <RadialButton label="과학 읽기" Icon={FlaskConical} onClick={goScience} color="purple" command="과학 점자 읽기" />
          </div>
          
          {/* 5. 하단: 사회 읽기 */}
          <div className="absolute -bottom-4 md:-bottom-6 left-1/2 transform -translate-x-1/2 z-10">
            <RadialButton label="사회 읽기" Icon={Building2} onClick={goSocial} color="orange" command="사회 점자 읽기" />
          </div>
          
          {/* 6. 왼쪽 하단: 어휘 읽기 */}
          <div className="absolute bottom-[12%] left-[12%] z-10">
            <RadialButton label="어휘 읽기" Icon={BookMarked} onClick={goVocab} color="teal" command="어휘 점자 읽기" />
          </div>
          
          {/* 7. 왼쪽: 속도 훈련 */}
          <div className="absolute top-1/2 left-0 transform translate-y-[-50%] z-10">
            <RadialButton label="속도 훈련" Icon={Gauge} onClick={goBrailleSpeed} color="pink" command="점자 속도 훈련" />
          </div>
        </nav>
      </div>

      {/* 안내 메시지 */}
      <div className="mt-6 text-center">
        <p className="text-sm text-muted mb-3">
          중앙 로고를 길게 눌러 음성 명령을 사용하세요
        </p>
        <button
          onClick={() =>
            speak(
              '시각장애인 수능 학습 앱, 점글이 수능입니다. 메인화면에 수능특강 학습, 국어 지문 연습, 그래프 도표 해석, 문항 풀이 오답노트, 어휘 시사 학습, 점자 속도 훈련, 실전 모의고사, 시험시간 관리 모드가 있습니다. 모드를 선택해주세요.'
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
