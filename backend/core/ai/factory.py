"""
AI Client Factory
Strategy Pattern - 전략 선택
"""
import os
from typing import Optional
from .base import AIClient
from .gpt_client import GPTClient, GPTClientSingleton
from .gemini_client import GeminiClient, GeminiClientSingleton


class AIClientFactory:
    """AI 클라이언트 팩토리"""
    
    @staticmethod
    def create(provider: str = None) -> Optional[AIClient]:
        """
        AI 클라이언트 생성
        Args:
            provider: 'openai', 'gemini', 또는 None (자동 선택)
        Returns:
            AIClient 인스턴스 또는 None
        """
        if provider is None:
            # 환경변수에서 기본 제공자 확인
            provider = os.getenv('DEFAULT_AI_PROVIDER', 'gemini')
        
        provider = provider.lower()
        
        if provider == 'openai':
            singleton = GPTClientSingleton()
            return singleton.get_client()
        elif provider == 'gemini':
            singleton = GeminiClientSingleton()
            return singleton.get_client()
        else:
            # 기본값: Gemini 시도, 실패 시 OpenAI
            singleton = GeminiClientSingleton()
            client = singleton.get_client()
            if client and client.is_available():
                return client
            
            singleton = GPTClientSingleton()
            return singleton.get_client()
    
    @staticmethod
    def get_available_providers() -> list:
        """사용 가능한 AI 제공자 목록"""
        providers = []
        
        if GPTClient().is_available():
            providers.append('openai')
        
        if GeminiClient().is_available():
            providers.append('gemini')
        
        return providers


