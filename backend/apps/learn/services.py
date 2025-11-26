"""
Service Layer Pattern Implementation for Learn App
지문 분석 비즈니스 로직
"""
from typing import Dict, Optional, List
import json
import re
from core.ai.factory import AIClientFactory


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
            # 기타 오류
            return {
                'summary': passage[:200] + '...',
                'characters': [],
                'structure': f'분석 오류: {str(e)}',
                'keywords': [],
            }

