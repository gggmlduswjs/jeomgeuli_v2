"""
Service Layer Pattern Implementation for Explore App
정보 탐색 관련 비즈니스 로직
"""
from typing import Dict, List, Optional
from core.ai.factory import AIClientFactory


class ExploreService:
    """정보 탐색 관련 비즈니스 로직"""
    
    def __init__(self):
        self.ai_client = AIClientFactory.create(provider='gemini')
    
    def get_news_summary(self, query: str) -> Dict:
        """뉴스 요약 조회"""
        if not self.ai_client:
            return self._get_fallback_news_response(query)
        
        prompt = f"""
        사용자의 질문: "{query}"
        
        다음 형식으로 뉴스 5개를 요약해주세요:
        
        1. 각 뉴스마다 제목, 한 줄 요약, 링크(예시 링크) 제공
        2. 전체 요약문 작성
        3. 쉬운 말로 설명
        4. 핵심 키워드 2-3개 추출
        
        JSON 형식으로 응답:
        {{
            "mode": "news",
            "summary": "전체 뉴스 요약",
            "simple": "초등학생도 이해할 수 있는 쉬운 설명",
            "keywords": ["키워드1", "키워드2", "키워드3"],
            "cards": [
                {{
                    "title": "뉴스 제목 1",
                    "oneLine": "한 줄 요약",
                    "url": "https://example.com/news1"
                }},
                ...
            ]
        }}
        """
        
        try:
            response_text = self.ai_client.generate_text(prompt)
            return self._parse_news_response(response_text, query)
        except Exception as e:
            print(f"Error in get_news_summary: {e}")
            return self._get_fallback_news_response(query)
    
    def get_sisa_words(self, limit: int = 10) -> List[Dict]:
        """시사 용어 목록 조회"""
        # TODO: 실제 시사 용어 데이터베이스에서 조회
        # 현재는 더미 데이터 반환
        return [
            {
                'term': '디플레이션',
                'meaning': '물가가 지속적으로 하락하는 현상',
                'example': '경기 침체로 인한 디플레이션 우려가 커지고 있다.',
            },
            {
                'term': '인플레이션',
                'meaning': '물가가 지속적으로 상승하는 현상',
                'example': '원유 가격 상승으로 인플레이션 압력이 증가했다.',
            },
        ]
    
    def search_news(self, keyword: str, limit: int = 5) -> List[Dict]:
        """뉴스 검색"""
        # TODO: 실제 뉴스 API 연동
        # 현재는 AI를 통한 요약 반환
        result = self.get_news_summary(keyword)
        return result.get('cards', [])[:limit]
    
    def _parse_news_response(self, response_text: str, query: str) -> Dict:
        """뉴스 응답 파싱"""
        try:
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except Exception as e:
            print(f"Error parsing news response: {e}")
        
        # Fallback parsing
        return self._get_fallback_news_response(query)
    
    def _get_fallback_news_response(self, query: str) -> Dict:
        """뉴스 응답 폴백"""
        return {
            "mode": "news",
            "summary": f"'{query}'에 대한 뉴스를 검색 중입니다. 잠시 후 다시 시도해주세요.",
            "simple": "뉴스 검색 서비스가 일시적으로 불안정합니다.",
            "keywords": ["뉴스", "검색", "일시중단"],
            "cards": [
                {
                    "title": "서비스 점검 중",
                    "oneLine": "뉴스 서비스를 점검하고 있습니다",
                    "url": "#"
                }
            ]
        }


