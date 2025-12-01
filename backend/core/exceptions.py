"""
애플리케이션 예외 클래스
통일된 에러 처리 구조
"""
from typing import Optional


class AppException(Exception):
    """애플리케이션 예외 베이스 클래스"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        user_message: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.user_message = user_message or message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """에러를 딕셔너리로 변환"""
        return {
            'error': self.user_message,
            'code': self.error_code,
            'message': self.message,
            'details': self.details,
        }


class PDFProcessingException(AppException):
    """PDF 처리 예외"""
    
    def __init__(self, message: str, user_message: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=400,
            user_message=user_message or "PDF 파일 처리 중 오류가 발생했습니다.",
            error_code='PDF_PROCESSING_ERROR',
            details=details
        )


class BrailleConversionException(AppException):
    """점자 변환 예외"""
    
    def __init__(self, message: str, user_message: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=500,
            user_message=user_message or "점자 변환 중 오류가 발생했습니다.",
            error_code='BRAILLE_CONVERSION_ERROR',
            details=details
        )


class AIAnalysisException(AppException):
    """AI 분석 예외"""
    
    def __init__(self, message: str, user_message: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=500,
            user_message=user_message or "AI 분석 중 오류가 발생했습니다.",
            error_code='AI_ANALYSIS_ERROR',
            details=details
        )


class ValidationException(AppException):
    """입력 검증 예외"""
    
    def __init__(self, message: str, user_message: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=400,
            user_message=user_message or "입력 데이터가 올바르지 않습니다.",
            error_code='VALIDATION_ERROR',
            details=details
        )


class NotFoundException(AppException):
    """리소스 없음 예외"""
    
    def __init__(self, message: str, user_message: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=404,
            user_message=user_message or "요청한 리소스를 찾을 수 없습니다.",
            error_code='NOT_FOUND',
            details=details
        )

