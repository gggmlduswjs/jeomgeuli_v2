"""
선택지 논리 구조 분석 서비스
선택지의 논리 구조, 패러프레이즈, 부정/관계 분석
"""
from typing import Dict, List, Optional
import json
from core.ai.factory import AIClientFactory
from core.exceptions import AIAnalysisException
from ..repositories import ChoiceRepository, PassageRepository


class ChoiceAnalysisService:
    """선택지 논리 구조 분석 서비스"""
    
    def __init__(
        self,
        choice_repo: Optional[ChoiceRepository] = None,
        passage_repo: Optional[PassageRepository] = None
    ):
        self.choice_repo = choice_repo or ChoiceRepository()
        self.passage_repo = passage_repo or PassageRepository()
        self.ai_client = AIClientFactory.create(provider='gemini')
    
    def analyze_choice_logic(
        self,
        choice_id: int,
        passage_id: Optional[int] = None
    ) -> Dict:
        """
        선택지 논리 구조 분석
        
        Args:
            choice_id: 선택지 ID
            passage_id: 지문 ID (선택적)
        
        Returns:
            {
                'core_claim': '핵심 주장',
                'error_type': 'condition_mismatch' | 'logical_error' | 'factual_error' | 'none',
                'paraphrase_analysis': {...},
                'negation_analysis': {...},
                'relation_analysis': {...}
            }
        """
        choice = self.choice_repo.get_by_id(choice_id)
        if not choice:
            raise ValueError(f"Choice {choice_id} not found")
        
        passage_text = ""
        if passage_id:
            passage = self.passage_repo.get_by_id(passage_id)
            if passage:
                passage_text = passage.content
        
        if not self.ai_client:
            return {
                'core_claim': choice.text,
                'error_type': 'none',
                'paraphrase_analysis': {},
                'negation_analysis': {},
                'relation_analysis': {}
            }
        
        prompt = f"""
다음 선택지를 분석하여 논리 구조를 파악해주세요.

선택지:
{choice.text}

지문 (참고용):
{passage_text[:500] if passage_text else '없음'}

분석 항목:
1. 핵심 주장 (core_claim): 선택지가 말하는 핵심 내용
2. 오류 유형 (error_type):
   - condition_mismatch: 조건 불일치
   - logical_error: 논리 오류
   - factual_error: 사실 오류
   - none: 오류 없음 (정답일 수 있음)
3. 패러프레이즈 분석: 지문과의 표현 차이
4. 부정 분석: 부정 표현 사용 여부
5. 관계 분석: 지문과의 논리적 관계

JSON 형식으로 반환해주세요:
{{
  "core_claim": "핵심 주장",
  "error_type": "condition_mismatch",
  "paraphrase_analysis": {{
    "is_paraphrase": true,
    "similarity": 0.7,
    "differences": ["차이점1", "차이점2"]
  }},
  "negation_analysis": {{
    "has_negation": false,
    "negation_words": []
  }},
  "relation_analysis": {{
    "relation_type": "support" | "contradict" | "neutral",
    "evidence_sentences": [0, 1]
  }}
}}
"""
        
        try:
            result_text = self.ai_client.generate_text(prompt)
            
            # JSON 파싱
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(result_text)
            
            # DB에 저장
            self.choice_repo.update_analysis(choice, {
                'logic_structure': analysis
            })
            
            return analysis
        except Exception as e:
            raise AIAnalysisException(
                f'선택지 분석 실패: {str(e)}',
                user_message='선택지 분석 중 오류가 발생했습니다.'
            )
    
    def compare_choices(
        self,
        question_id: int,
        passage_id: Optional[int] = None
    ) -> Dict:
        """
        선택지 비교 분석 (병렬 비교)
        
        Returns:
            {
                'comparisons': [
                    {
                        'choice_number': 1,
                        'core_claim': '...',
                        'error_type': '...',
                        'evidence_sentences': [...],
                        'is_correct': False
                    },
                    ...
                ]
            }
        """
        from ..repositories import QuestionRepository, ChoiceRepository
        question_repo = QuestionRepository()
        choice_repo = ChoiceRepository()
        
        question = question_repo.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        choices = choice_repo.get_by_question(question_id)
        if not choices:
            return {'comparisons': []}
        
        passage_text = ""
        if passage_id:
            passage = self.passage_repo.get_by_id(passage_id)
            if passage:
                passage_text = passage.content
        
        if not self.ai_client:
            return {
                'comparisons': [
                    {
                        'choice_number': c.order,
                        'core_claim': c.text,
                        'error_type': 'unknown',
                        'evidence_sentences': [],
                        'is_correct': c.is_correct
                    }
                    for c in choices
                ]
            }
        
        choices_text = '\n'.join([
            f"{c.order}번: {c.text}"
            for c in choices
        ])
        
        prompt = f"""
다음 문항의 선택지들을 비교 분석해주세요.

문항:
{question.question_text}

지문:
{passage_text[:1000] if passage_text else '없음'}

선택지:
{choices_text}

각 선택지에 대해:
1. 핵심 주장
2. 오류 유형 (정답이면 'none')
3. 근거 문장 인덱스 (지문에서)
4. 정답 여부

JSON 형식으로 반환해주세요:
{{
  "comparisons": [
    {{
      "choice_number": 1,
      "core_claim": "핵심 주장",
      "error_type": "condition_mismatch",
      "evidence_sentences": [0, 2],
      "is_correct": false
    }},
    ...
  ]
}}
"""
        
        try:
            result_text = self.ai_client.generate_text(prompt)
            
            # JSON 파싱
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            comparisons = result.get('comparisons', [])
            
            # 각 선택지의 분석 결과 업데이트
            for comp in comparisons:
                choice_num = comp.get('choice_number')
                choice = next((c for c in choices if c.order == choice_num), None)
                if choice:
                    self.choice_repo.update_analysis(choice, {
                        'logic_structure': {
                            'core_claim': comp.get('core_claim', ''),
                            'error_type': comp.get('error_type', 'none')
                        },
                        'evidence_sentences': comp.get('evidence_sentences', [])
                    })
            
            return {'comparisons': comparisons}
        except Exception as e:
            raise AIAnalysisException(
                f'선택지 비교 분석 실패: {str(e)}',
                user_message='선택지 비교 분석 중 오류가 발생했습니다.'
            )
    
    def analyze_wrong_answer(
        self,
        choice_id: int,
        passage_id: Optional[int] = None
    ) -> Dict:
        """
        오답 분석 (왜 틀렸는지 설명)
        
        Returns:
            {
                'reason': '오답 이유',
                'corrected_claim': '수정된 주장',
                'evidence_contradiction': '모순되는 근거'
            }
        """
        choice = self.choice_repo.get_by_id(choice_id)
        if not choice:
            raise ValueError(f"Choice {choice_id} not found")
        
        if choice.is_correct:
            return {
                'reason': '정답입니다',
                'corrected_claim': choice.text,
                'evidence_contradiction': ''
            }
        
        passage_text = ""
        if passage_id:
            passage = self.passage_repo.get_by_id(passage_id)
            if passage:
                passage_text = passage.content
        
        if not self.ai_client:
            return {
                'reason': '분석 불가',
                'corrected_claim': choice.text,
                'evidence_contradiction': ''
            }
        
        prompt = f"""
다음 선택지가 왜 오답인지 분석해주세요.

선택지:
{choice.text}

지문:
{passage_text[:1000] if passage_text else '없음'}

분석 항목:
1. 오답 이유
2. 수정된 주장 (정답에 가까운 표현)
3. 모순되는 근거 문장

JSON 형식으로 반환해주세요:
{{
  "reason": "오답 이유",
  "corrected_claim": "수정된 주장",
  "evidence_contradiction": "모순되는 근거"
}}
"""
        
        try:
            result_text = self.ai_client.generate_text(prompt)
            
            # JSON 파싱
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(result_text)
            
            # DB에 저장
            self.choice_repo.update_analysis(choice, {
                'wrong_answer_analysis': analysis
            })
            
            return analysis
        except Exception as e:
            raise AIAnalysisException(
                f'오답 분석 실패: {str(e)}',
                user_message='오답 분석 중 오류가 발생했습니다.'
            )

