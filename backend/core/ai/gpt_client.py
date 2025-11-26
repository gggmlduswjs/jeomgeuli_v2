"""
OpenAI GPT Client Implementation
Strategy Pattern - OpenAI 전략
"""
import os
from typing import Dict, Optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import AIClient


class GPTClient(AIClient):
    """OpenAI GPT 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key and OPENAI_AVAILABLE:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """OpenAI 사용 가능 여부"""
        return OPENAI_AVAILABLE and self.api_key is not None and self.client is not None
    
    def generate_text(self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> str:
        """텍스트 생성"""
        if not self.is_available():
            raise ValueError("OpenAI client is not available")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def analyze_image(self, image_data: bytes, prompt: str = "") -> Dict:
        """이미지 분석 (Vision API)"""
        if not self.is_available():
            raise ValueError("OpenAI client is not available")
        
        # TODO: Vision API 구현
        # 현재는 텍스트만 지원
        raise NotImplementedError("Vision API not yet implemented")


class GPTClientSingleton:
    """OpenAI 클라이언트 싱글톤"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self) -> Optional[GPTClient]:
        """클라이언트 인스턴스 반환"""
        if self._client is None:
            self._client = GPTClient()
        return self._client if self._client.is_available() else None


