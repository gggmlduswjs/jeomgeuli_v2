"""
Service Layer Pattern Implementation for Learn App
지문 분석 비즈니스 로직
"""
from typing import Dict, Optional, List
import json
import re
from core.ai.factory import AIClientFactory
from core.exceptions import AIAnalysisException


class PassageAnalysisService:
    """지문 분석 비즈니스 로직"""
    
    def __init__(self):
        # Strategy Pattern: AI 클라이언트 팩토리 사용
        self.ai_client = AIClientFactory.create(provider='gemini')
    
    def analyze_passage(self, passage: str) -> Dict:
        """
        지문 분석 및 구조화
        - 요약 추출
        - 등장인물/개념 추출
        - 구조 분석
        - 키워드 추출
        """
        if not self.ai_client:
            # AI 클라이언트가 없으면 기본 구조 반환
            return {
                'summary': passage[:200] + '...',
                'characters': [],
                'structure': 'AI 분석 불가 (API 키 미설정)',
                'keywords': [],
            }
        
        prompt = f"""
다음 국어 지문을 분석하여 구조화된 형태로 제공해주세요.

요구사항:
1. 지문의 핵심 주제와 요지를 한 문장으로 요약
2. 주요 등장인물/개념 나열
3. 지문의 구조 (서론, 본론, 결론 등)
4. 중요한 키워드 5개 추출

지문:
{passage}

JSON 형식으로 반환해주세요:
{{
  "summary": "요약",
  "characters": ["인물1", "인물2"],
  "structure": "구조 설명",
  "keywords": ["키워드1", "키워드2", ...]
}}
"""
        
        try:
            result_text = self.ai_client.generate_text(prompt)
            
            # JSON 파싱
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            structure = json.loads(result_text)
            return structure
            
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 구조
            return {
                'summary': result_text[:200] if 'result_text' in locals() else passage[:200],
                'characters': [],
                'structure': '구조 분석 실패',
                'keywords': [],
            }
        except Exception as e:
            raise AIAnalysisException(
                f'지문 분석 실패: {str(e)}',
                user_message='지문 분석 중 오류가 발생했습니다.'
            )
    
    def split_paragraphs(self, passage: str) -> List[Dict]:
        """
        문단 단위 분할 및 기능 분석
        Returns:
            [
                {
                    'id': 1,
                    'text': '문단 내용',
                    'type': 'introduction' | 'development' | 'example' | 'conclusion',
                    'start_sentence': 0,
                    'end_sentence': 5
                },
                ...
            ]
        """
        if not self.ai_client:
            # 기본 분할 (빈 줄 기준)
            paragraphs = [p.strip() for p in passage.split('\n\n') if p.strip()]
            return [
                {
                    'id': i + 1,
                    'text': p,
                    'type': 'unknown',
                    'start_sentence': i,
                    'end_sentence': i
                }
                for i, p in enumerate(paragraphs)
            ]
        
        prompt = f"""
다음 지문을 문단 단위로 분할하고 각 문단의 기능을 분석해주세요.

지문:
{passage}

각 문단의 기능 유형:
- introduction: 도입부
- development: 전개부
- example: 예시/설명
- conclusion: 결론부

JSON 형식으로 반환해주세요:
{{
  "paragraphs": [
    {{
      "id": 1,
      "text": "문단 내용",
      "type": "introduction",
      "start_sentence": 0,
      "end_sentence": 2
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
            return result.get('paragraphs', [])
        except Exception as e:
            raise AIAnalysisException(
                f'문단 분할 실패: {str(e)}',
                user_message='문단 분석 중 오류가 발생했습니다.'
            )
    
    def extract_central_sentences(self, passage: str, count: int = 3) -> List[int]:
        """
        중심 문장 추출
        Returns:
            문장 인덱스 리스트
        """
        # 간단한 구현: 문장 분리 후 AI로 중요도 판단
        sentences = re.split(r'[.!?]\s+', passage)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not self.ai_client or len(sentences) <= count:
            # 문장이 적으면 처음 N개 반환
            return list(range(min(count, len(sentences))))
        
        prompt = f"""
다음 지문에서 가장 중요한 {count}개의 중심 문장을 선택해주세요.

지문:
{passage}

각 문장의 인덱스(0부터 시작)를 JSON 배열로 반환해주세요:
{{
  "central_sentences": [0, 2, 5]
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
            indices = result.get('central_sentences', [])
            # 유효한 인덱스만 반환
            return [i for i in indices if 0 <= i < len(sentences)][:count]
        except Exception as e:
            # 실패 시 처음 N개 반환
            return list(range(min(count, len(sentences))))
    
    def extract_keywords(self, passage: str, max_count: int = 5) -> List[str]:
        """
        핵심 키워드 추출
        """
        if not self.ai_client:
            # 기본 키워드 추출 (빈도 기반)
            words = re.findall(r'[가-힣]{2,}', passage)
            from collections import Counter
            counter = Counter(words)
            return [word for word, _ in counter.most_common(max_count)]
        
        prompt = f"""
다음 지문에서 가장 중요한 키워드 {max_count}개를 추출해주세요.

지문:
{passage}

JSON 형식으로 반환해주세요:
{{
  "keywords": ["키워드1", "키워드2", ...]
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
            return result.get('keywords', [])[:max_count]
        except Exception as e:
            # 실패 시 기본 추출
            words = re.findall(r'[가-힣]{2,}', passage)
            from collections import Counter
            counter = Counter(words)
            return [word for word, _ in counter.most_common(max_count)]
    
    def classify_question_type(self, question_text: str) -> str:
        """
        문항 유형 분류
        Returns:
            'inference' | 'detail' | 'main_idea' | 'purpose' | 'attitude' | 'flow' | 'vocab'
        """
        if not self.ai_client:
            return 'unknown'
        
        prompt = f"""
다음 문항의 유형을 분류해주세요.

문항:
{question_text}

유형:
- inference: 추론형
- detail: 세부 내용
- main_idea: 주제/제목
- purpose: 목적
- attitude: 태도/어조
- flow: 문장 삽입
- vocab: 어휘/표현

JSON 형식으로 반환해주세요:
{{
  "type": "inference"
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
            return result.get('type', 'unknown')
        except Exception as e:
            return 'unknown'

