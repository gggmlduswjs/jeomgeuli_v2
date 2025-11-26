"""
Google Gemini Client Implementation
Strategy Pattern - Gemini 전략
"""
import os
from typing import Dict, Optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base import AIClient


class GeminiClient(AIClient):
    """Google Gemini 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def is_available(self) -> bool:
        """Gemini 사용 가능 여부"""
        return GEMINI_AVAILABLE and self.api_key is not None and self.model is not None
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """텍스트 생성"""
        if not self.is_available():
            raise ValueError("Gemini client is not available")
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def analyze_image(self, image_data: bytes, prompt: str = "") -> Dict:
        """이미지 분석"""
        if not self.is_available():
            raise ValueError("Gemini client is not available")
        
        try:
            import PIL.Image
            import io
            
            image = PIL.Image.open(io.BytesIO(image_data))
            
            analysis_prompt = prompt or "이 그래프나 도표를 분석하여 다음 정보를 추출해주세요: 추세(증가/감소/유지), 극대/극소점, 주요 비교값. JSON 형식으로 반환해주세요."
            
            response = self.model.generate_content([analysis_prompt, image])
            result_text = response.text.strip()
            
            # JSON 파싱 시도
            import json
            try:
                if '```json' in result_text:
                    result_text = result_text.split('```json')[1].split('```')[0].strip()
                elif '```' in result_text:
                    result_text = result_text.split('```')[1].split('```')[0].strip()
                
                patterns = json.loads(result_text)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 구조
                patterns = {
                    'trend': 'stable',
                    'extremum': 'none',
                    'comparison': 'equal',
                }
            
            return patterns
            
        except Exception as e:
            raise Exception(f"Gemini Vision API error: {str(e)}")


class GeminiClientSingleton:
    """Gemini 클라이언트 싱글톤"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self) -> Optional[GeminiClient]:
        """클라이언트 인스턴스 반환"""
        if self._client is None:
            self._client = GeminiClient()
        return self._client if self._client.is_available() else None


