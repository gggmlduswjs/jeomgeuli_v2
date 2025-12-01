"""
문항-근거 매핑 서비스
LLM 기반 의미 유사도 계산 및 근거 문장 매핑
"""
from typing import Dict, List, Optional, Tuple
import json
from core.ai.factory import AIClientFactory
from core.exceptions import AIAnalysisException
from ..repositories import (
    PassageRepository, EvidenceMappingRepository, QuestionRepository
)


class EvidenceMappingService:
    """문항-근거 매핑 서비스"""
    
    def __init__(
        self,
        passage_repo: Optional[PassageRepository] = None,
        evidence_repo: Optional[EvidenceMappingRepository] = None,
        question_repo: Optional[QuestionRepository] = None
    ):
        self.passage_repo = passage_repo or PassageRepository()
        self.evidence_repo = evidence_repo or EvidenceMappingRepository()
        self.question_repo = question_repo or QuestionRepository()
        self.ai_client = AIClientFactory.create(provider='gemini')
    
    def map_question_to_evidence(
        self,
        question_id: int,
        passage_id: Optional[int] = None,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        문항-근거 매핑 알고리즘
        
        Args:
            question_id: 문제 ID
            passage_id: 지문 ID (None이면 문제에 연결된 지문 자동 탐색)
            threshold: 유사도 임계값 (0.0 ~ 1.0)
        
        Returns:
            [
                {
                    'passage_sentence_id': 0,
                    'similarity_score': 0.85,
                    'mapping_type': 'direct',
                    'context_sentences': [0, 1, 2]
                },
                ...
            ]
        """
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        # 지문 찾기
        if passage_id:
            passage = self.passage_repo.get_by_id(passage_id)
        else:
            # 문제에 연결된 지문 자동 탐색
            passages = self.passage_repo.get_by_question(question_id)
            if not passages:
                return []
            passage = passages[0]  # 첫 번째 지문 사용
        
        if not passage:
            return []
        
        # 문장 분리
        sentences = passage.sentences if passage.sentences else []
        if not sentences:
            # 문장이 없으면 기본 분리
            import re
            sentence_texts = re.split(r'[.!?]\s+', passage.content)
            sentences = [
                {'id': i, 'text': text.strip(), 'index': i}
                for i, text in enumerate(sentence_texts)
                if text.strip()
            ]
        
        # LLM 기반 의미 유사도 계산
        mappings = self._calculate_similarity(question.question_text, sentences, threshold)
        
        # DB에 저장
        evidence_mappings = []
        for mapping in mappings:
            evidence = self.evidence_repo.create(
                question=question,
                passage=passage,
                passage_sentence_id=mapping['passage_sentence_id'],
                similarity_score=mapping['similarity_score'],
                mapping_type=mapping['mapping_type'],
                context_sentences=mapping.get('context_sentences', [])
            )
            evidence_mappings.append({
                'id': evidence.id,
                'passage_sentence_id': evidence.passage_sentence_id,
                'similarity_score': evidence.similarity_score,
                'mapping_type': evidence.mapping_type,
                'context_sentences': evidence.context_sentences,
            })
        
        return evidence_mappings
    
    def _calculate_similarity(
        self,
        question_text: str,
        sentences: List[Dict],
        threshold: float
    ) -> List[Dict]:
        """의미 유사도 계산"""
        if not self.ai_client:
            # AI 클라이언트가 없으면 기본 매핑 (첫 번째 문장)
            return [{
                'passage_sentence_id': 0,
                'similarity_score': 0.5,
                'mapping_type': 'direct',
                'context_sentences': [0]
            }]
        
        # 문장 텍스트 추출
        sentence_texts = [s.get('text', '') for s in sentences]
        
        prompt = f"""
다음 문항과 지문의 각 문장 간 의미 유사도를 계산해주세요.

문항:
{question_text}

지문 문장들:
{json.dumps(sentence_texts, ensure_ascii=False, indent=2)}

각 문장에 대해:
1. 문항과의 의미 유사도 점수 (0.0 ~ 1.0)
2. 매핑 타입 (direct: 직접 근거, inference: 추론 근거, contradiction: 모순, support: 지지)
3. 주변 문장 인덱스 (앞뒤 1-2개 문장)

JSON 형식으로 반환해주세요:
{{
  "mappings": [
    {{
      "sentence_index": 0,
      "similarity_score": 0.85,
      "mapping_type": "direct",
      "context_sentences": [0, 1]
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
            mappings = result.get('mappings', [])
            
            # 임계값 이상인 것만 필터링
            filtered = [
                {
                    'passage_sentence_id': m['sentence_index'],
                    'similarity_score': float(m['similarity_score']),
                    'mapping_type': m.get('mapping_type', 'direct'),
                    'context_sentences': m.get('context_sentences', [m['sentence_index']])
                }
                for m in mappings
                if float(m.get('similarity_score', 0)) >= threshold
            ]
            
            # 유사도 점수 순으로 정렬
            filtered.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return filtered
        except Exception as e:
            raise AIAnalysisException(
                f'의미 유사도 계산 실패: {str(e)}',
                user_message='근거 매핑 분석 중 오류가 발생했습니다.'
            )
    
    def map_choice_to_evidence(
        self,
        choice_id: int,
        passage_id: int,
        threshold: float = 0.4
    ) -> List[Dict]:
        """
        선택지별 근거 문장 분리
        
        Args:
            choice_id: 선택지 ID
            passage_id: 지문 ID
            threshold: 유사도 임계값
        
        Returns:
            근거 문장 매핑 리스트
        """
        from ..repositories import ChoiceRepository
        choice_repo = ChoiceRepository()
        
        choice = choice_repo.get_by_id(choice_id)
        if not choice:
            raise ValueError(f"Choice {choice_id} not found")
        
        passage = self.passage_repo.get_by_id(passage_id)
        if not passage:
            raise ValueError(f"Passage {passage_id} not found")
        
        # 선택지와 지문 문장 간 유사도 계산
        sentences = passage.sentences if passage.sentences else []
        if not sentences:
            import re
            sentence_texts = re.split(r'[.!?]\s+', passage.content)
            sentences = [
                {'id': i, 'text': text.strip(), 'index': i}
                for i, text in enumerate(sentence_texts)
                if text.strip()
            ]
        
        mappings = self._calculate_similarity(choice.text, sentences, threshold)
        
        # 선택지의 evidence_sentences 업데이트
        evidence_sentence_ids = [m['passage_sentence_id'] for m in mappings]
        choice_repo.update_analysis(choice, {
            'evidence_sentences': evidence_sentence_ids
        })
        
        return mappings

