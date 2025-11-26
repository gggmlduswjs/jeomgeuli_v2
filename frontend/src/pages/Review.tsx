import { useEffect, useState, useRef, useMemo, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, RotateCcw, Mic, MicOff, Check, X } from "lucide-react";
// import { api } from "@/lib/http";
import { type Cell } from "@/lib/brailleSafe";
import { normalizeCells } from "@/lib/brailleSafe";
import { learningAPI } from "../lib/api/LearningAPI";
import { brailleAPI } from "../lib/api/BrailleAPI";
import useTTS from "../hooks/useTTS";
import useVoiceCommands from "../hooks/useVoiceCommands";
import AppShellMobile from "../components/ui/AppShellMobile";
import VoiceService from "../services/VoiceService";
import { useVoiceStore, selectIsListening, selectTranscript } from "../store/voice";
import BrailleDot from '../components/braille/BrailleDot';

// 점자 셀 표시 컴포넌트 (퀴즈와 동일)
const Dot = BrailleDot;
function CellView({ c }: { c: Cell }) {
  // 안전한 배열 구조분해할당
  const cellArray = Array.isArray(c) && c.length >= 6 ? c : [0,0,0,0,0,0];
  const [a,b,c2,d,e,f] = cellArray;
  
  return (
    <div className="inline-flex flex-col px-3 py-2 rounded-xl border border-border bg-white shadow-toss">
      <div className="flex"><Dot on={!!a}/><Dot on={!!d}/></div>
      <div className="flex"><Dot on={!!b}/><Dot on={!!e}/></div>
      <div className="flex"><Dot on={!!c2}/><Dot on={!!f}/></div>
    </div>
  );
}

// 🎯 STT 결과와 정답을 유연하게 매칭하는 함수 (퀴즈와 동일)
function isAnswerMatch(userInput: string, correctAnswer: string, item: any): boolean {
  const normalizedUser = userInput.trim().toLowerCase();
  const normalizedCorrect = correctAnswer.trim().toLowerCase();
  
  // 1) 정확한 매칭
  if (normalizedUser === normalizedCorrect) return true;
  
  // 2) 자모 특별 처리: "기역" ↔ "ㄱ" 양방향 매칭
  const char = item.char?.trim();
  const name = item.name?.trim();
  
  if (char && name) {
    // "기역"이라고 말했는데 STT가 "ㄱ"으로 인식한 경우
    if ((normalizedUser === char.toLowerCase() && normalizedCorrect === name.toLowerCase()) ||
        // "ㄱ"이라고 말했는데 STT가 "기역"으로 인식한 경우  
        (normalizedUser === name.toLowerCase() && normalizedCorrect === char.toLowerCase())) {
      return true;
    }
  }
  
  // 3) 부분 매칭 (예: "기역"에서 "기"만 인식된 경우)
  if (normalizedCorrect.includes(normalizedUser) || normalizedUser.includes(normalizedCorrect)) {
    return true;
  }
  
  return false;
}

export default function Review() {
  const navigate = useNavigate();
  const { speak } = useTTS();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState("");
  const [showAnswer, setShowAnswer] = useState(false);
  const [result, setResult] = useState<null | { ok: boolean; answer: string }>(null);
  const [_completed, _setCompleted] = useState<number[]>([]);
  const [score, setScore] = useState({ correct: 0, total: 0 });

  // STT - VoiceService 사용 (선택자로 최적화)
  const isListening = useVoiceStore(selectIsListening);
  const transcript = useVoiceStore(selectTranscript);
  const inputRef = useRef<HTMLInputElement>(null);

  // 페이지 진입 시 자동 음성 안내
  useEffect(() => {
    const welcomeMessage = '복습 모드입니다. 이전에 틀린 문제들을 다시 복습해보세요.';
    
    const timer = setTimeout(() => {
      speak(welcomeMessage);
    }, 500);

    return () => {
      clearTimeout(timer);
    };
  }, [speak]);

  // 뒤로가기 버튼 클릭 시 홈으로 이동
  const handleBack = () => {
    navigate('/');
  };

  // 제목과 진행률 표시
  const headerTitle = items.length > 0 
    ? `복습 (${currentIdx + 1}/${items.length})` 
    : '복습';

  // 데이터 로딩
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        // 1) 서버 목록 시도 (LearningAPI 사용)
        const reviewItems = await learningAPI.listReviewItems();
        console.log('[Review] API response items:', reviewItems.length);
        if (reviewItems.length > 0) {
          console.log('[Review] Loaded items:', reviewItems.length);
          setItems(reviewItems);
          setLoading(false);
          return;
        } else {
          console.log('[Review] No items in response');
        }
      } catch (error) {
        console.error('[Review] 서버 목록 로드 실패:', error);
      }

      // 2) 로컬 폴백
      try {
        const local = JSON.parse(localStorage.getItem('review:pending') || '[]');
        if (Array.isArray(local) && local.length > 0) {
          console.log('[Review] Using local fallback:', local.length, 'items');
          setItems(local.reverse()); // 최신 먼저
        } else {
          console.log('[Review] No local data available');
          setItems([]);
        }
      } catch (error) {
        console.error('[Review] 로컬 데이터 로드 실패:', error);
        setItems([]);
      }
      setLoading(false);
    })();
  }, []);

  // 음성 명령 처리
  const { onSpeech } = useVoiceCommands({
    home: () => {
      VoiceService.stopSTT();
      navigate('/');
    },
    back: () => {
      VoiceService.stopSTT();
      navigate('/');
    },
    submit: () => {
      if (userAnswer.trim()) {
        onSubmit();
      } else {
        speak("정답을 말하거나 입력해주세요.");
      }
    },
    clear: () => {
      setUserAnswer("");
      inputRef.current?.focus();
    },
    next: () => {
      if (currentIdx + 1 < items.length) {
        setCurrentIdx(prev => prev + 1);
        setUserAnswer("");
        inputRef.current?.focus();
      } else {
        speak("마지막 문제입니다.");
      }
    },
    repeat: () => {
      if (currentItem) {
        const p = currentItem.payload ?? currentItem;
        const text = p.content?.trim() || p.text?.trim() || p.word?.trim() || "";
        if (text) {
          speak(`문제: ${text}`);
        }
      }
    },
    stop: () => {
      if (isListening) stopSTT();
    },
  });

  // STT 결과 처리 - 명령 우선, 아니면 정답으로 처리
  useEffect(() => {
    if (!transcript) return;
    
    // 1) 먼저 음성 명령 처리 시도 (홈, 뒤로, 반복 등)
    const handled = onSpeech(transcript);
    if (handled) {
      // 명령이 처리되었으면 transcript 초기화하고 종료
      useVoiceStore.getState().resetTranscript();
      return;
    }
    
    // 2) 명령이 아니면 정답으로 처리
    setUserAnswer(transcript);
    setTimeout(() => onSubmit(transcript), 50);
  }, [transcript, onSpeech]);

  const currentItem = items[currentIdx];
  
  // 현재 항목의 고유 키 (무한 루프 방지용)
  const currentItemKey = useMemo(() => {
    if (!currentItem) return null;
    return currentItem?.id || currentItem?.timestamp || `${currentIdx}-${currentItem?.payload?.content || ''}`;
  }, [currentItem?.id, currentItem?.timestamp, currentIdx, currentItem?.payload?.content]);
  
  // 점자 데이터 정규화: 안전한 배열 처리
  const [cells, setCells] = useState<Cell[]>([]);
  const [cellsLoading, setCellsLoading] = useState(false);
  
  // 점자 셀 로드 (없으면 자동 변환)
  useEffect(() => {
    if (!currentItem) {
      setCells([]);
      setCellsLoading(false);
      return;
    }
    
    const p = currentItem?.payload ?? currentItem;
    const text = p?.content?.trim() || p?.text?.trim() || p?.word?.trim() || "";
    
    // 이미 셀이 있으면 사용
    const existingCells = currentItem?.payload?.cells || currentItem?.payload?.questionCells || [];
    if (Array.isArray(existingCells) && existingCells.length > 0) {
      const normalized = existingCells.filter(cell => Array.isArray(cell) && cell.length === 6) as Cell[];
      setCells(normalized);
      setCellsLoading(false);
      return;
    }
    
    // 셀이 없고 텍스트가 있으면 변환
    if (text) {
      setCellsLoading(true);
      let cancelled = false;
      
      (async () => {
        try {
          const result = await brailleAPI.convertBraille(text, 'word');
          if (!cancelled) {
            if (result.ok && result.cells && Array.isArray(result.cells)) {
              const normalized = normalizeCells(result.cells) as Cell[];
              setCells(normalized);
            } else {
              setCells([]);
            }
          }
        } catch (error) {
          if (!cancelled) {
            console.error('[Review] 점자 변환 실패:', error);
            setCells([]);
          }
        } finally {
          if (!cancelled) {
            setCellsLoading(false);
          }
        }
      })();
      
      return () => {
        cancelled = true;
      };
    } else {
      setCells([]);
      setCellsLoading(false);
    }
  }, [currentItemKey]); // rawCells 제거, currentItemKey만 사용

  const startSTT = useCallback(async () => {
    try {
      await VoiceService.startSTT({
        onResult: (text) => {
          setUserAnswer(text);
          setTimeout(() => onSubmit(text), 50);
        },
        onError: (error) => {
          console.error('[Review] STT error:', error);
          speak('음성 인식에 실패했습니다. 다시 시도해주세요.');
        },
        autoStop: true,
      });
    } catch (e) {
      console.error('[Review] STT start error:', e);
      speak('음성 인식을 시작할 수 없습니다.');
    }
  }, [speak]);

  const stopSTT = useCallback(() => {
    VoiceService.stopSTT();
  }, []);

  const onSubmit = async (val?: string) => {
    if (!currentItem) return;
    const p = currentItem.payload ?? currentItem;
    // 백엔드에서 반환하는 필드: content, text, expected 등
    const answer = p.expected?.trim() || p.content?.trim() || p.text?.trim() || "";
    const userAns = (val ?? userAnswer).trim();

    const ok = userAns.length > 0 && isAnswerMatch(userAns, answer, p);
    
    setResult({ ok, answer });
    setScore(prev => ({ 
      correct: prev.correct + (ok ? 1 : 0), 
      total: prev.total + 1 
    }));

    setTimeout(() => {
      setResult(null);
      setUserAnswer("");
      setShowAnswer(false);
      
      if (currentIdx + 1 < items.length) {
        setCurrentIdx(prev => prev + 1);
        inputRef.current?.focus();
      } else {
        // 복습 완료
        alert(`복습 완료! 정답률: ${Math.round((score.correct + (ok ? 1 : 0)) / (score.total + 1) * 100)}%`);
        navigate("/", { replace: true });
      }
    }, 1500);
  };

  const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter") onSubmit();
  };

  const showAnswerNow = () => {
    setShowAnswer(true);
    const p = currentItem?.payload ?? currentItem;
    const answer = p?.expected?.trim() || p?.content?.trim() || p?.text?.trim() || "";
    if (answer) speak(answer);
  };

  if (loading) {
    return (
      <AppShellMobile title="로딩 중..." showBackButton onBack={handleBack}>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
            <div className="text-muted">복습 목록을 불러오는 중…</div>
          </div>
        </div>
      </AppShellMobile>
    );
  }
  
  if (!items.length) {
    return (
      <AppShellMobile title="복습" showBackButton onBack={handleBack}>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="w-full md:max-w-md md:mx-auto text-center space-y-4">
            <div className="bg-white rounded-2xl p-6 shadow-toss">
              <div className="text-6xl mb-3">📚</div>
              <h2 className="text-xl font-semibold text-fg mb-1.5">
                오늘은 복습할 항목이 없습니다
              </h2>
              <p className="text-muted mb-4">
                퀴즈에서 틀린 문제나 정보탐색에서 저장한 키워드가 복습 목록에 추가됩니다.
              </p>
              <div className="space-y-2.5">
                <button
                  onClick={() => navigate('/learn')}
                  className="w-full px-4 py-2 rounded-2xl bg-primary text-white hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 active:scale-95"
                >
                  학습하기로 이동
                </button>
                <button
                  onClick={() => navigate('/explore')}
                  className="w-full px-4 py-2 rounded-2xl bg-accent text-white hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent transition-all duration-200 active:scale-95"
                >
                  정보탐색으로 이동
                </button>
                <button
                  onClick={() => navigate('/')}
                  className="w-full px-4 py-2 rounded-2xl bg-card text-fg border border-border hover:bg-border focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 active:scale-95"
                >
                  홈으로 돌아가기
                </button>
              </div>
            </div>
          </div>
        </div>
      </AppShellMobile>
    );
  }

  const progress = Math.round(((currentIdx + 1) / items.length) * 100);
  const p = currentItem?.payload ?? currentItem;
  const titleWithProgress = `복습 (${currentIdx + 1}/${items.length})`;

  return (
    <AppShellMobile title={titleWithProgress} showBackButton onBack={handleBack}>
      <div className="space-y-4">
        {/* 진행률 */}
        <div className="bg-white rounded-2xl p-3 shadow-toss">
          <div className="flex justify-between text-sm text-muted mb-1.5">
            <span>진척도</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-border rounded-full h-2">
            <div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
          <div className="text-xs text-muted mt-2 text-center">
            정답률: {score.total > 0 ? Math.round(score.correct / score.total * 100) : 0}%
          </div>
        </div>

        {/* 문제 카드 */}
        <div className="bg-white rounded-2xl p-4 shadow-toss text-center">
          {/* 결과 배지 */}
          {result && (
            <div className="mb-3 w-full flex justify-center">
              <div className={`px-3 py-1.5 rounded-xl text-sm ${
                result.ok ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
              }`}>
                {result.ok ? (
                  <><Check className="inline w-4 h-4 mr-1" />정답입니다!</>
                ) : (
                  <><X className="inline w-4 h-4 mr-1" />오답입니다. 정답: {result.answer}</>
                )}
              </div>
            </div>
          )}

          {/* 점자 셀 표출 */}
          <div className="mb-4 flex justify-center">
            {cellsLoading ? (
              <div className="text-muted text-sm py-8">
                <div className="animate-pulse">점자 변환 중...</div>
              </div>
            ) : cells.length > 0 ? (
              <div className="inline-flex flex-wrap justify-center gap-3">
                {cells.map((c, idx) => <CellView key={idx} c={c} />)}
              </div>
            ) : (
              <div className="text-muted text-sm py-8">
                <div>점자 데이터 없음</div>
                <div className="text-xs mt-2">
                  {(() => {
                    const p = currentItem?.payload ?? currentItem;
                    return p?.content?.trim() || p?.text?.trim() || p?.word?.trim() || '데이터 없음';
                  })()}
                </div>
              </div>
            )}
          </div>

          {/* 답 표시 또는 입력 */}
          {showAnswer ? (
            <div className="text-2xl font-bold text-green-600 mb-3">
              {p?.expected?.trim() || p?.content?.trim() || p?.text?.trim() || "정답 없음"}
            </div>
          ) : (
            <>
              <label className="block text-sm text-muted mb-1.5">정답 입력</label>
              <input
                ref={inputRef}
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="정확히 입력하세요"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-card focus:outline-none focus:ring-2 focus:ring-primary"
                autoFocus
              />
            </>
          )}

          <div className="flex gap-2 mt-3">
            <button
              onClick={showAnswerNow}
              className="flex-1 px-4 py-2 rounded-2xl bg-accent text-white hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent transition-all duration-200 active:scale-95"
            >
              <RotateCcw className="inline w-4 h-4 mr-1" /> 답 보기
            </button>

            {/* 음성 입력 토글 */}
            <button
              onClick={isListening ? stopSTT : startSTT}
              className={`px-4 py-2 rounded-2xl ${isListening ? "bg-danger text-white" : "bg-card text-fg"} hover:bg-border focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 active:scale-95`}
              aria-pressed={isListening}
              title="음성으로 정답 말하기"
            >
              {isListening ? <><MicOff className="inline w-4 h-4 mr-1" /> 끄기</> : <><Mic className="inline w-4 h-4 mr-1" /> 음성 입력</>}
            </button>

            <button
              onClick={() => onSubmit()}
              disabled={!userAnswer.trim().length}
              className="flex-1 px-4 py-2 rounded-2xl bg-primary text-white hover:bg-primary/90 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200 active:scale-95"
            >
              제출
            </button>
          </div>
        </div>
      </div>
    </AppShellMobile>
  );
}