"""
PDF 파서 모듈
PyPDF2/PyMuPDF 기반 PDF 텍스트 추출 및 레이아웃 분석
"""
import io
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from abc import ABC, abstractmethod

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from core.exceptions import PDFProcessingException


class PDFParserStrategy(ABC):
    """PDF 파서 전략 인터페이스 (Strategy Pattern)"""
    
    @abstractmethod
    def extract_text(self, pdf_file) -> str:
        """텍스트 추출"""
        pass
    
    @abstractmethod
    def detect_image_areas(self, pdf_file) -> List[Dict]:
        """이미지 영역 감지"""
        pass
    
    @abstractmethod
    def analyze_layout(self, pdf_file) -> Dict:
        """레이아웃 분석"""
        pass


class PyPDF2Strategy(PDFParserStrategy):
    """PyPDF2 기반 파서 전략"""
    
    def extract_text(self, pdf_file) -> str:
        """PyPDF2로 텍스트 추출"""
        if not PYPDF2_AVAILABLE:
            raise PDFProcessingException(
                'PyPDF2가 설치되지 않았습니다',
                user_message='PDF 파서 라이브러리가 설치되지 않았습니다.'
            )
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    print(f"[PyPDF2Strategy] 페이지 추출 실패: {e}")
                    continue
            return text
        except PyPDF2.errors.PdfReadError as e:
            raise PDFProcessingException(
                f'PDF 파일 읽기 실패: {str(e)}',
                user_message='PDF 파일이 손상되었거나 읽을 수 없습니다.'
            )
    
    def detect_image_areas(self, pdf_file) -> List[Dict]:
        """이미지 영역 감지 (PyPDF2는 제한적 지원)"""
        # PyPDF2는 이미지 추출을 직접 지원하지 않음
        # 기본 구조만 반환
        return []
    
    def analyze_layout(self, pdf_file) -> Dict:
        """레이아웃 분석 (PyPDF2는 제한적 지원)"""
        if not PYPDF2_AVAILABLE:
            raise PDFProcessingException('PyPDF2가 설치되지 않았습니다')
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            layout_info = {
                'page_count': len(pdf_reader.pages),
                'pages': []
            }
            
            for i, page in enumerate(pdf_reader.pages):
                page_info = {
                    'page_number': i + 1,
                    'text_blocks': [],
                    'image_blocks': []
                }
                # PyPDF2는 상세 레이아웃 정보를 제공하지 않음
                layout_info['pages'].append(page_info)
            
            return layout_info
        except PyPDF2.errors.PdfReadError as e:
            raise PDFProcessingException(
                f'PDF 레이아웃 분석 실패: {str(e)}',
                user_message='PDF 파일 분석 중 오류가 발생했습니다.'
            )


class PyMuPDFStrategy(PDFParserStrategy):
    """PyMuPDF 기반 파서 전략 (더 강력한 기능)"""
    
    def extract_text(self, pdf_file) -> str:
        """PyMuPDF로 텍스트 추출"""
        if not PYMUPDF_AVAILABLE:
            raise PDFProcessingException(
                'PyMuPDF가 설치되지 않았습니다',
                user_message='PDF 파서 라이브러리가 설치되지 않았습니다.'
            )
        
        try:
            # 파일을 바이트로 읽기
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # 파일 포인터 리셋
            
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            
            doc.close()
            return text
        except Exception as e:
            raise PDFProcessingException(
                f'PDF 파일 읽기 실패: {str(e)}',
                user_message='PDF 파일이 손상되었거나 읽을 수 없습니다.'
            )
    
    def detect_image_areas(self, pdf_file) -> List[Dict]:
        """이미지 영역 감지"""
        if not PYMUPDF_AVAILABLE:
            return []
        
        try:
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
            
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            image_areas = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # 이미지 영역 정보
                    image_rects = page.get_image_rects(xref)
                    for rect in image_rects:
                        image_areas.append({
                            'page': page_num + 1,
                            'index': img_index,
                            'x0': rect.x0,
                            'y0': rect.y0,
                            'x1': rect.x1,
                            'y1': rect.y1,
                            'width': rect.width,
                            'height': rect.height,
                            'type': 'image',
                            'size': len(image_bytes)
                        })
            
            doc.close()
            return image_areas
        except Exception as e:
            print(f"[PyMuPDFStrategy] 이미지 영역 감지 실패: {e}")
            return []
    
    def analyze_layout(self, pdf_file) -> Dict:
        """레이아웃 분석"""
        if not PYMUPDF_AVAILABLE:
            raise PDFProcessingException('PyMuPDF가 설치되지 않았습니다')
        
        try:
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
            
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            layout_info = {
                'page_count': len(doc),
                'pages': []
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 텍스트 블록 추출
                text_blocks = page.get_text("blocks")
                blocks = []
                
                for block in text_blocks:
                    if len(block) >= 5:  # [x0, y0, x1, y1, "text", ...]
                        blocks.append({
                            'type': 'text',
                            'x0': block[0],
                            'y0': block[1],
                            'x1': block[2],
                            'y1': block[3],
                            'text': block[4] if len(block) > 4 else '',
                        })
                
                # 이미지 블록 추출
                image_list = page.get_images()
                image_blocks = []
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    image_rects = page.get_image_rects(xref)
                    for rect in image_rects:
                        image_blocks.append({
                            'type': 'image',
                            'x0': rect.x0,
                            'y0': rect.y0,
                            'x1': rect.x1,
                            'y1': rect.y1,
                        })
                
                layout_info['pages'].append({
                    'page_number': page_num + 1,
                    'text_blocks': blocks,
                    'image_blocks': image_blocks,
                })
            
            doc.close()
            return layout_info
        except Exception as e:
            raise PDFProcessingException(
                f'PDF 레이아웃 분석 실패: {str(e)}',
                user_message='PDF 파일 분석 중 오류가 발생했습니다.'
            )


class PDFParser:
    """PDF 파서 (Factory Pattern으로 전략 선택)"""
    
    def __init__(self, strategy: Optional[str] = None):
        """
        Args:
            strategy: 'pypdf2' 또는 'pymupdf' (None이면 자동 선택)
        """
        if strategy == 'pymupdf' and PYMUPDF_AVAILABLE:
            self.strategy = PyMuPDFStrategy()
        elif strategy == 'pypdf2' and PYPDF2_AVAILABLE:
            self.strategy = PyPDF2Strategy()
        elif PYMUPDF_AVAILABLE:
            # 기본값: PyMuPDF (더 강력함)
            self.strategy = PyMuPDFStrategy()
        elif PYPDF2_AVAILABLE:
            self.strategy = PyPDF2Strategy()
        else:
            raise PDFProcessingException(
                'PDF 파서 라이브러리가 설치되지 않았습니다',
                user_message='PDF 파서 라이브러리(PyPDF2 또는 PyMuPDF)를 설치해주세요.'
            )
    
    def extract_text(self, pdf_file) -> str:
        """텍스트 추출"""
        return self.strategy.extract_text(pdf_file)
    
    def detect_image_areas(self, pdf_file) -> List[Dict]:
        """이미지 영역 감지 (그래프/표/도형)"""
        return self.strategy.detect_image_areas(pdf_file)
    
    def analyze_layout(self, pdf_file) -> Dict:
        """레이아웃 분석 (문단/박스/번호/선택지)"""
        return self.strategy.analyze_layout(pdf_file)
    
    def extract_blocks(self, pdf_file) -> Dict:
        """
        PDF를 블록 단위로 분할
        Returns:
            {
                'text_blocks': [...],
                'image_blocks': [...],
                'question_blocks': [...],
                'choice_blocks': [...]
            }
        """
        layout = self.analyze_layout(pdf_file)
        
        # 블록 구조화
        blocks = {
            'text_blocks': [],
            'image_blocks': [],
            'question_blocks': [],
            'choice_blocks': []
        }
        
        for page_info in layout['pages']:
            # 텍스트 블록
            for block in page_info.get('text_blocks', []):
                text = block.get('text', '').strip()
                if text:
                    # 간단한 패턴 매칭으로 문항/선택지 감지
                    if self._is_question_block(text):
                        blocks['question_blocks'].append({
                            **block,
                            'page': page_info['page_number']
                        })
                    elif self._is_choice_block(text):
                        blocks['choice_blocks'].append({
                            **block,
                            'page': page_info['page_number']
                        })
                    else:
                        blocks['text_blocks'].append({
                            **block,
                            'page': page_info['page_number']
                        })
            
            # 이미지 블록
            for block in page_info.get('image_blocks', []):
                blocks['image_blocks'].append({
                    **block,
                    'page': page_info['page_number']
                })
        
        return blocks
    
    def _is_question_block(self, text: str) -> bool:
        """문항 블록인지 판단"""
        import re
        # 패턴: "1.", "①", "문항 1" 등
        patterns = [
            r'^\d+[\.\)]\s*',  # "1. ", "1) "
            r'^문항\s*\d+',  # "문항 1"
            r'^\([가-힣]\)',  # "(가)"
        ]
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        return False
    
    def _is_choice_block(self, text: str) -> bool:
        """선택지 블록인지 판단"""
        import re
        # 패턴: "①", "1)", "(1)" 등
        patterns = [
            r'^[①②③④⑤]\s*',  # "① "
            r'^\d+[\)\.]\s*',  # "1) ", "1. "
            r'^\([1-5]\)\s*',  # "(1) "
        ]
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        return False

