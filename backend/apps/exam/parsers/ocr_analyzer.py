"""
OCR 분석 모듈
Tesseract/EasyOCR 기반 이미지 텍스트 인식 및 레이아웃 분석
"""
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import io

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from core.exceptions import PDFProcessingException


class OCRStrategy(ABC):
    """OCR 전략 인터페이스 (Strategy Pattern)"""
    
    @abstractmethod
    def recognize_text(self, image_data: bytes, lang: str = 'kor+eng') -> str:
        """텍스트 인식"""
        pass
    
    @abstractmethod
    def recognize_with_layout(self, image_data: bytes, lang: str = 'kor+eng') -> Dict:
        """레이아웃 정보와 함께 텍스트 인식"""
        pass


class TesseractOCRStrategy(OCRStrategy):
    """Tesseract OCR 전략"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Args:
            tesseract_cmd: Tesseract 실행 파일 경로 (Windows의 경우 필요)
        """
        if not TESSERACT_AVAILABLE:
            raise PDFProcessingException(
                'Tesseract OCR이 설치되지 않았습니다',
                user_message='OCR 라이브러리가 설치되지 않았습니다.'
            )
        
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def recognize_text(self, image_data: bytes, lang: str = 'kor+eng') -> str:
        """텍스트 인식"""
        try:
            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except Exception as e:
            raise PDFProcessingException(
                f'Tesseract OCR 실패: {str(e)}',
                user_message='이미지 텍스트 인식 중 오류가 발생했습니다.'
            )
    
    def recognize_with_layout(self, image_data: bytes, lang: str = 'kor+eng') -> Dict:
        """레이아웃 정보와 함께 텍스트 인식"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # 텍스트 추출
            text = pytesseract.image_to_string(image, lang=lang)
            
            # 레이아웃 정보 추출
            data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            
            # 블록 구조화
            blocks = []
            current_block = None
            
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    block_info = {
                        'text': data['text'][i],
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'level': data['level'][i],
                        'page_num': data['page_num'][i],
                        'block_num': data['block_num'][i],
                        'par_num': data['par_num'][i],
                        'line_num': data['line_num'][i],
                        'word_num': data['word_num'][i],
                    }
                    blocks.append(block_info)
            
            return {
                'text': text.strip(),
                'blocks': blocks,
                'confidence': self._calculate_confidence(data)
            }
        except Exception as e:
            raise PDFProcessingException(
                f'Tesseract OCR 레이아웃 분석 실패: {str(e)}',
                user_message='이미지 레이아웃 분석 중 오류가 발생했습니다.'
            )
    
    def _calculate_confidence(self, data: dict) -> float:
        """평균 신뢰도 계산"""
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        if confidences:
            return sum(confidences) / len(confidences)
        return 0.0


class EasyOCRStrategy(OCRStrategy):
    """EasyOCR 전략"""
    
    def __init__(self, languages: List[str] = ['ko', 'en']):
        """
        Args:
            languages: 인식할 언어 리스트 ['ko', 'en']
        """
        if not EASYOCR_AVAILABLE:
            raise PDFProcessingException(
                'EasyOCR이 설치되지 않았습니다',
                user_message='OCR 라이브러리가 설치되지 않았습니다.'
            )
        
        try:
            self.reader = easyocr.Reader(languages)
        except Exception as e:
            raise PDFProcessingException(
                f'EasyOCR 초기화 실패: {str(e)}',
                user_message='OCR 엔진 초기화 중 오류가 발생했습니다.'
            )
    
    def recognize_text(self, image_data: bytes, lang: str = 'kor+eng') -> str:
        """텍스트 인식"""
        try:
            results = self.reader.readtext(image_data)
            text = '\n'.join([result[1] for result in results])
            return text.strip()
        except Exception as e:
            raise PDFProcessingException(
                f'EasyOCR 실패: {str(e)}',
                user_message='이미지 텍스트 인식 중 오류가 발생했습니다.'
            )
    
    def recognize_with_layout(self, image_data: bytes, lang: str = 'kor+eng') -> Dict:
        """레이아웃 정보와 함께 텍스트 인식"""
        try:
            results = self.reader.readtext(image_data)
            
            blocks = []
            full_text = []
            
            for result in results:
                bbox, text, confidence = result
                # bbox는 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] 형식
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                blocks.append({
                    'text': text,
                    'x': min(x_coords),
                    'y': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords),
                    'confidence': confidence,
                    'bbox': bbox
                })
                full_text.append(text)
            
            return {
                'text': '\n'.join(full_text).strip(),
                'blocks': blocks,
                'confidence': sum([b['confidence'] for b in blocks]) / len(blocks) if blocks else 0.0
            }
        except Exception as e:
            raise PDFProcessingException(
                f'EasyOCR 레이아웃 분석 실패: {str(e)}',
                user_message='이미지 레이아웃 분석 중 오류가 발생했습니다.'
            )


class OCRAnalyzer:
    """OCR 분석기 (Factory Pattern으로 전략 선택)"""
    
    def __init__(self, strategy: Optional[str] = None, **kwargs):
        """
        Args:
            strategy: 'tesseract' 또는 'easyocr' (None이면 자동 선택)
            **kwargs: 전략별 추가 옵션
                - tesseract_cmd: Tesseract 실행 파일 경로
                - languages: EasyOCR 언어 리스트
        """
        if strategy == 'tesseract' and TESSERACT_AVAILABLE:
            self.strategy = TesseractOCRStrategy(
                tesseract_cmd=kwargs.get('tesseract_cmd')
            )
        elif strategy == 'easyocr' and EASYOCR_AVAILABLE:
            self.strategy = EasyOCRStrategy(
                languages=kwargs.get('languages', ['ko', 'en'])
            )
        elif TESSERACT_AVAILABLE:
            # 기본값: Tesseract
            self.strategy = TesseractOCRStrategy(
                tesseract_cmd=kwargs.get('tesseract_cmd')
            )
        elif EASYOCR_AVAILABLE:
            self.strategy = EasyOCRStrategy(
                languages=kwargs.get('languages', ['ko', 'en'])
            )
        else:
            raise PDFProcessingException(
                'OCR 라이브러리가 설치되지 않았습니다',
                user_message='OCR 라이브러리(Tesseract 또는 EasyOCR)를 설치해주세요.'
            )
    
    def recognize_text(self, image_data: bytes, lang: str = 'kor+eng') -> str:
        """텍스트 인식"""
        return self.strategy.recognize_text(image_data, lang)
    
    def recognize_with_layout(self, image_data: bytes, lang: str = 'kor+eng') -> Dict:
        """레이아웃 정보와 함께 텍스트 인식"""
        return self.strategy.recognize_with_layout(image_data, lang)
    
    def correct_text(self, extracted_text: str, ocr_text: str) -> str:
        """
        추출된 텍스트를 OCR 결과로 보정
        OCR이 더 정확한 경우 사용
        """
        # 간단한 보정 로직 (실제로는 더 정교한 알고리즘 필요)
        if len(ocr_text) > len(extracted_text) * 0.8:
            # OCR 텍스트가 충분히 길면 사용
            return ocr_text
        return extracted_text

