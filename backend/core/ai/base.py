"""
AI Client Abstract Base Class
Strategy Pattern을 위한 인터페이스 정의
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class AIClient(ABC):
    """AI 클라이언트 추상 기본 클래스"""
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        텍스트 생성
        Args:
            prompt: 프롬프트
            **kwargs: 추가 옵션
        Returns:
            생성된 텍스트
        """
        pass
    
    @abstractmethod
    def analyze_image(self, image_data: bytes, prompt: str = "") -> Dict:
        """
        이미지 분석
        Args:
            image_data: 이미지 바이너리 데이터
            prompt: 분석 프롬프트
        Returns:
            분석 결과 딕셔너리
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """AI 서비스 사용 가능 여부"""
        pass


