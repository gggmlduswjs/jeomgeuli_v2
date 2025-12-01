"""
Braille Encoding Engine
3셀 점자 변환 및 의미 청킹
"""
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from utils.braille_converter import text_to_cells
from core.exceptions import BrailleConversionException
from ..repositories import BrailleChunkRepository, BrailleContent
from ..models import BrailleChunk


class ChunkingStrategy(ABC):
    """청킹 전략 인터페이스 (Strategy Pattern)"""
    
    @abstractmethod
    def chunk_text(self, text: str, max_chunk_size: int = 3) -> List[Dict]:
        """
        텍스트를 의미 단위로 청킹
        
        Args:
            text: 원본 텍스트
            max_chunk_size: 최대 청크 크기 (셀 수)
        
        Returns:
            [
                {
                    'text': '청크 텍스트',
                    'start': 0,
                    'end': 10,
                    'semantic_type': 'sentence' | 'word' | 'formula' | 'keyword'
                },
                ...
            ]
        """
        pass


class SentenceChunkingStrategy(ChunkingStrategy):
    """문장 단위 청킹 전략 (국어용)"""
    
    def chunk_text(self, text: str, max_chunk_size: int = 3) -> List[Dict]:
        """문장 단위로 분할"""
        import re
        
        # 문장 분리
        sentences = re.split(r'[.!?]\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_pos = 0
        
        for sentence in sentences:
            if not sentence:
                continue
            
            # 문장을 점자로 변환하여 셀 수 계산
            cells = text_to_cells(sentence)
            cell_count = len(cells)
            
            # 3셀 이하면 그대로 하나의 청크
            if cell_count <= max_chunk_size:
                chunks.append({
                    'text': sentence,
                    'start': current_pos,
                    'end': current_pos + len(sentence),
                    'semantic_type': 'sentence',
                    'cell_count': cell_count
                })
                current_pos += len(sentence) + 1  # +1 for separator
            else:
                # 긴 문장은 단어 단위로 분할
                words = sentence.split()
                word_chunks = []
                for word in words:
                    word_cells = text_to_cells(word)
                    if len(word_cells) <= max_chunk_size:
                        word_chunks.append({
                            'text': word,
                            'start': current_pos,
                            'end': current_pos + len(word),
                            'semantic_type': 'word',
                            'cell_count': len(word_cells)
                        })
                        current_pos += len(word) + 1
                
                chunks.extend(word_chunks)
        
        return chunks


class WordChunkingStrategy(ChunkingStrategy):
    """단어 단위 청킹 전략 (영어용)"""
    
    def chunk_text(self, text: str, max_chunk_size: int = 3) -> List[Dict]:
        """단어 단위로 분할"""
        import re
        
        # 단어 분리
        words = re.findall(r'\b\w+\b', text)
        
        chunks = []
        current_pos = 0
        
        for word in words:
            cells = text_to_cells(word)
            cell_count = len(cells)
            
            if cell_count <= max_chunk_size:
                chunks.append({
                    'text': word,
                    'start': current_pos,
                    'end': current_pos + len(word),
                    'semantic_type': 'word',
                    'cell_count': cell_count
                })
            else:
                # 긴 단어는 문자 단위로 분할
                for char in word:
                    char_cells = text_to_cells(char)
                    if len(char_cells) <= max_chunk_size:
                        chunks.append({
                            'text': char,
                            'start': current_pos,
                            'end': current_pos + len(char),
                            'semantic_type': 'word',
                            'cell_count': len(char_cells)
                        })
                        current_pos += len(char)
            
            # 다음 단어 위치 찾기
            next_pos = text.find(word, current_pos)
            if next_pos != -1:
                current_pos = next_pos + len(word)
            else:
                current_pos += len(word)
        
        return chunks


class SmartChunkingStrategy(ChunkingStrategy):
    """스마트 청킹 전략 (수학용: 수식 중심)"""
    
    def chunk_text(self, text: str, max_chunk_size: int = 3) -> List[Dict]:
        """수식 중심으로 분할"""
        import re
        from utils.content_extractor import extract_formula, contains_formula
        
        chunks = []
        current_pos = 0
        
        # 수식 추출
        formula = extract_formula(text)
        
        if formula:
            # 수식이 있으면 수식과 나머지로 분할
            formula_pos = text.find(formula)
            
            # 수식 이전 텍스트
            if formula_pos > current_pos:
                before_text = text[current_pos:formula_pos]
                before_chunks = self._chunk_regular_text(before_text, current_pos, max_chunk_size)
                chunks.extend(before_chunks)
                current_pos = formula_pos
            
            # 수식 처리
            formula_cells = text_to_cells(formula)
            if len(formula_cells) <= max_chunk_size:
                chunks.append({
                    'text': formula,
                    'start': current_pos,
                    'end': current_pos + len(formula),
                    'semantic_type': 'formula',
                    'cell_count': len(formula_cells)
                })
            else:
                # 긴 수식은 부분으로 분할
                formula_parts = self._split_formula(formula, max_chunk_size)
                for part in formula_parts:
                    part_cells = text_to_cells(part)
                    chunks.append({
                        'text': part,
                        'start': current_pos,
                        'end': current_pos + len(part),
                        'semantic_type': 'formula',
                        'cell_count': len(part_cells)
                    })
                    current_pos += len(part)
            
            current_pos += len(formula)
        
        # 나머지 텍스트 처리
        if current_pos < len(text):
            remaining_text = text[current_pos:]
            remaining_chunks = self._chunk_regular_text(remaining_text, current_pos, max_chunk_size)
            chunks.extend(remaining_chunks)
        
        return chunks if chunks else self._chunk_regular_text(text, 0, max_chunk_size)
    
    def _chunk_regular_text(self, text: str, start_pos: int, max_chunk_size: int) -> List[Dict]:
        """일반 텍스트 청킹"""
        import re
        
        # 키워드 추출
        from utils.content_extractor import extract_keywords
        keywords = extract_keywords(text, max_count=5)
        
        chunks = []
        current_pos = start_pos
        
        # 키워드 중심으로 청킹
        for keyword in keywords:
            keyword_pos = text.find(keyword, current_pos - start_pos)
            if keyword_pos != -1:
                keyword_pos += start_pos
                
                # 키워드 이전 텍스트
                if keyword_pos > current_pos:
                    before_text = text[current_pos - start_pos:keyword_pos - start_pos]
                    before_chunks = self._simple_chunk(before_text, current_pos, max_chunk_size)
                    chunks.extend(before_chunks)
                
                # 키워드
                keyword_cells = text_to_cells(keyword)
                if len(keyword_cells) <= max_chunk_size:
                    chunks.append({
                        'text': keyword,
                        'start': keyword_pos,
                        'end': keyword_pos + len(keyword),
                        'semantic_type': 'keyword',
                        'cell_count': len(keyword_cells)
                    })
                    current_pos = keyword_pos + len(keyword)
        
        # 남은 텍스트
        if current_pos - start_pos < len(text):
            remaining = text[current_pos - start_pos:]
            remaining_chunks = self._simple_chunk(remaining, current_pos, max_chunk_size)
            chunks.extend(remaining_chunks)
        
        return chunks
    
    def _simple_chunk(self, text: str, start_pos: int, max_chunk_size: int) -> List[Dict]:
        """간단한 청킹 (공백 기준)"""
        words = text.split()
        chunks = []
        current_pos = start_pos
        
        for word in words:
            cells = text_to_cells(word)
            if len(cells) <= max_chunk_size:
                chunks.append({
                    'text': word,
                    'start': current_pos,
                    'end': current_pos + len(word),
                    'semantic_type': 'word',
                    'cell_count': len(cells)
                })
                current_pos += len(word) + 1
        
        return chunks
    
    def _split_formula(self, formula: str, max_chunk_size: int) -> List[str]:
        """수식 분할"""
        # 간단한 구현: 연산자 기준으로 분할
        import re
        parts = re.split(r'([+\-*/=<>≤≥])', formula)
        return [p for p in parts if p.strip()]


class KeywordChunkingStrategy(ChunkingStrategy):
    """키워드 중심 청킹 전략"""
    
    def chunk_text(self, text: str, max_chunk_size: int = 3) -> List[Dict]:
        """키워드 중심으로 분할"""
        from utils.content_extractor import extract_keywords
        
        keywords = extract_keywords(text, max_count=10)
        
        if not keywords:
            # 키워드가 없으면 문장 단위
            strategy = SentenceChunkingStrategy()
            return strategy.chunk_text(text, max_chunk_size)
        
        chunks = []
        current_pos = 0
        
        for keyword in keywords:
            keyword_pos = text.find(keyword, current_pos)
            if keyword_pos == -1:
                continue
            
            # 키워드 이전 텍스트 (간단히 스킵)
            # 키워드만 추출
            keyword_cells = text_to_cells(keyword)
            if len(keyword_cells) <= max_chunk_size:
                chunks.append({
                    'text': keyword,
                    'start': keyword_pos,
                    'end': keyword_pos + len(keyword),
                    'semantic_type': 'keyword',
                    'cell_count': len(keyword_cells)
                })
            
            current_pos = keyword_pos + len(keyword)
        
        return chunks if chunks else SentenceChunkingStrategy().chunk_text(text, max_chunk_size)


class BrailleEncodingEngine:
    """Braille Encoding Engine (3셀 점자 변환)"""
    
    def __init__(self, chunk_repo: Optional[BrailleChunkRepository] = None):
        self.chunk_repo = chunk_repo or BrailleChunkRepository()
        
        # 전략 팩토리 (Strategy Pattern)
        self.strategies = {
            'korean': SentenceChunkingStrategy(),
            'english': WordChunkingStrategy(),
            'math': SmartChunkingStrategy(),
            'science': KeywordChunkingStrategy(),
            'social': KeywordChunkingStrategy(),
        }
    
    def encode_semantic_chunks(
        self,
        text: str,
        subject: str = 'korean',
        max_cells: int = 3
    ) -> List[Dict]:
        """
        의미 단위 청킹
        
        Args:
            text: 원본 텍스트
            subject: 과목 ('korean', 'english', 'math', 'science', 'social')
            max_cells: 최대 셀 수 (기본 3)
        
        Returns:
            [
                {
                    'text': '청크 텍스트',
                    'cells': [[1,0,0,0,0,0], [1,1,0,0,0,0], [1,0,0,1,0,0]],
                    'semantic_type': 'sentence',
                    'start': 0,
                    'end': 10
                },
                ...
            ]
        """
        # 전략 선택
        strategy = self.strategies.get(subject, self.strategies['korean'])
        
        # 텍스트 청킹
        text_chunks = strategy.chunk_text(text, max_chunk_size=max_cells)
        
        # 각 청크를 점자로 변환
        semantic_chunks = []
        for chunk in text_chunks:
            chunk_text = chunk['text']
            cells = text_to_cells(chunk_text)
            
            # 3-cell 패킷 생성
            packets = self.generate_3cell_packets(cells, max_cells)
            
            semantic_chunks.append({
                'text': chunk_text,
                'cells': cells,
                'packets': packets,  # 3-cell 패킷 리스트
                'semantic_type': chunk.get('semantic_type', 'sentence'),
                'start': chunk.get('start', 0),
                'end': chunk.get('end', len(chunk_text)),
                'cell_count': len(cells)
            })
        
        return semantic_chunks
    
    def generate_3cell_packets(
        self,
        cells: List[List[int]],
        max_cells: int = 3
    ) -> List[List[List[int]]]:
        """
        3-cell 패킷 생성
        
        Args:
            cells: 점자 셀 배열 [[1,0,0,0,0,0], ...]
            max_cells: 패킷당 최대 셀 수 (기본 3)
        
        Returns:
            [
                [[1,0,0,0,0,0], [1,1,0,0,0,0], [1,0,0,1,0,0]],  # 패킷 1 (3셀)
                [[1,0,0,1,1,0], [1,0,0,0,1,0]],  # 패킷 2 (2셀)
                ...
            ]
        """
        packets = []
        
        for i in range(0, len(cells), max_cells):
            packet = cells[i:i + max_cells]
            # 패킷이 max_cells보다 작으면 패딩 (선택적)
            # 여기서는 그대로 반환
            packets.append(packet)
        
        return packets
    
    def create_braille_chunks(
        self,
        braille_content: BrailleContent,
        text: str,
        subject: str = 'korean',
        passage_id: Optional[int] = None,
        question_id: Optional[int] = None,
        choice_id: Optional[int] = None
    ) -> List[BrailleChunk]:
        """
        BrailleChunk 모델 생성
        
        Args:
            braille_content: BrailleContent 인스턴스
            text: 원본 텍스트
            subject: 과목
            passage_id: 지문 ID (선택적)
            question_id: 문제 ID (선택적)
            choice_id: 선택지 ID (선택적)
        
        Returns:
            생성된 BrailleChunk 리스트
        """
        # 의미 청킹
        semantic_chunks = self.encode_semantic_chunks(text, subject)
        
        # BrailleChunk 생성
        chunks = []
        for idx, semantic_chunk in enumerate(semantic_chunks):
            # 3-cell 패킷 선택 (첫 번째 패킷 사용)
            packets = semantic_chunk.get('packets', [])
            packet = packets[0] if packets else semantic_chunk['cells'][:3]
            
            # 패킷이 3셀 미만이면 패딩
            while len(packet) < 3:
                packet.append([0, 0, 0, 0, 0, 0])
            packet = packet[:3]  # 최대 3셀만
            
            chunk = self.chunk_repo.create(
                content=braille_content,
                passage_id=passage_id,
                question_id=question_id,
                choice_id=choice_id,
                chunk_index=idx,
                cells=packet,
                semantic_type=semantic_chunk['semantic_type'],
                original_text=semantic_chunk['text'],
                start_position=semantic_chunk.get('start'),
                end_position=semantic_chunk.get('end')
            )
            chunks.append(chunk)
        
        return chunks

