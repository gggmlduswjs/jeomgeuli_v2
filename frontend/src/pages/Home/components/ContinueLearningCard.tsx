/**
 * 오늘 학습 이어하기 카드
 * 보호자용 시각 UI + 시각장애인용 음성 안내
 */
import { useNavigate } from 'react-router-dom';
import { BookOpen, Play } from 'lucide-react';

interface ContinueLearningCardProps {
  currentLearning?: {
    subject: 'korean' | 'english' | 'math' | null;
    textbook: string;
    progress: { passages: number; questions: number };
  };
  onContinue?: () => void;
}

export default function ContinueLearningCard({
  currentLearning,
  onContinue
}: ContinueLearningCardProps) {
  const navigate = useNavigate();

  const handleContinue = () => {
    if (onContinue) {
      onContinue();
    } else if (currentLearning?.subject) {
      navigate(`/textbook?subject=${currentLearning.subject}`);
    }
  };

  if (!currentLearning) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border-2 border-dashed border-gray-300">
        <div className="flex items-center gap-3 mb-4">
          <BookOpen className="w-6 h-6 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-500">오늘 학습 이어하기</h3>
        </div>
        <p className="text-gray-400 text-sm">진행 중인 학습이 없습니다.</p>
      </div>
    );
  }

  const subjectNames = {
    korean: '국어',
    english: '영어',
    math: '수학'
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-md p-6 border-2 border-blue-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <BookOpen className="w-6 h-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">오늘 학습 이어하기</h3>
        </div>
        <button
          onClick={handleContinue}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          aria-label="학습 이어하기"
        >
          <Play className="w-4 h-4" />
          <span>계속하기</span>
        </button>
      </div>
      
      <div className="space-y-2">
        <div>
          <p className="text-sm text-gray-600 mb-1">현재 학습</p>
          <p className="text-base font-medium text-gray-800">
            {subjectNames[currentLearning.subject || 'korean']} - {currentLearning.textbook}
          </p>
        </div>
        
        <div className="flex gap-4 text-sm">
          <div>
            <span className="text-gray-600">지문 </span>
            <span className="font-semibold text-blue-600">
              {currentLearning.progress.passages}개 완료
            </span>
          </div>
          <div>
            <span className="text-gray-600">문항 </span>
            <span className="font-semibold text-blue-600">
              {currentLearning.progress.questions}개 완료
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

