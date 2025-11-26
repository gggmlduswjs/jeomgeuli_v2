"""
Service Layer Pattern Implementation for Braille App
점자 패턴 생성 비즈니스 로직
"""
from typing import Dict, List, Optional
import re
from utils.braille_converter import text_to_cells


class BraillePatternService:
    """점자 패턴 생성 비즈니스 로직"""
    
    # 패턴 매핑 (3-cell display용)
    PATTERNS = {
        'answer_correct': [0, 0, 1, 0, 0, 0],  # 정답: ○○●
        'answer_wrong': [1, 0, 0, 0, 0, 0],    # 오답: ●○○
        'trend_increase': [1, 0, 0, 0, 0, 0],  # 증가: ●○○
        'trend_decrease': [0, 0, 1, 0, 0, 0],   # 감소: ○○●
        'trend_stable': [0, 1, 0, 0, 0, 0],     # 유지: ○●○
        'extremum_maximum': [1, 0, 1, 0, 0, 0], # 극대: ●○●
        'extremum_minimum': [0, 1, 0, 1, 0, 0], # 극소: ○●○●
        'status_start': [1, 1, 1, 0, 0, 0],     # 시작: ●●●
        'status_pause': [0, 1, 0, 0, 1, 0],     # 일시정지: ○●○○●
        'status_stop': [0, 0, 0, 0, 0, 0],      # 정지: 빈 패턴
    }
    
    NUMBER_PATTERNS = {
        1: [1, 0, 0, 0, 0, 0],
        2: [1, 1, 0, 0, 0, 0],
        3: [1, 0, 0, 1, 0, 0],
        4: [1, 0, 0, 1, 1, 0],
        5: [1, 0, 0, 0, 1, 0],
    }
    
    def generate_pattern(self, pattern_type: str, data: Dict = None) -> List[int]:
        """
        패턴 생성
        pattern_type: 'answer', 'trend', 'number', 'status', 'extremum'
        """
        if pattern_type == 'answer':
            is_correct = data.get('is_correct', False) if data else False
            return self.PATTERNS['answer_correct' if is_correct else 'answer_wrong']
        
        elif pattern_type == 'trend':
            trend = data.get('trend', 'stable') if data else 'stable'
            if trend == 'increase':
                return self.PATTERNS['trend_increase']
            elif trend == 'decrease':
                return self.PATTERNS['trend_decrease']
            else:
                return self.PATTERNS['trend_stable']
        
        elif pattern_type == 'number':
            num = data.get('number', 1) if data else 1
            return self.NUMBER_PATTERNS.get(num, [0, 0, 0, 0, 0, 0])
        
        elif pattern_type == 'status':
            status = data.get('status', 'stop') if data else 'stop'
            if status == 'start':
                return self.PATTERNS['status_start']
            elif status == 'pause':
                return self.PATTERNS['status_pause']
            else:
                return self.PATTERNS['status_stop']
        
        elif pattern_type == 'extremum':
            extremum_type = data.get('type', 'maximum') if data else 'maximum'
            if extremum_type == 'maximum':
                return self.PATTERNS['extremum_maximum']
            else:
                return self.PATTERNS['extremum_minimum']
        
        else:
            # 알 수 없는 타입
            return [0, 0, 0, 0, 0, 0]
    
    def validate_pattern(self, pattern: List[int]) -> bool:
        """패턴 유효성 검증"""
        if not isinstance(pattern, list):
            return False
        if len(pattern) != 6:
            return False
        return all(dot in [0, 1] for dot in pattern)
    
    def convert_formula_to_braille(self, formula: str) -> List[List[int]]:
        """
        수식을 점자로 변환
        수식 패턴 감지 및 최적화된 점자 변환
        """
        if not formula:
            return []
        
        # 수식 패턴 정규화 (예: x² -> x^2, ∫ -> integral 등)
        normalized = formula
        
        # 지수 패턴 정규화
        normalized = re.sub(r'([a-zA-Z])\s*²', r'\1^2', normalized)
        normalized = re.sub(r'([a-zA-Z])\s*³', r'\1^3', normalized)
        normalized = re.sub(r'([a-zA-Z])\s*⁴', r'\1^4', normalized)
        
        # 점자 변환
        cells = text_to_cells(normalized)
        return cells
    
    def extract_formula_from_text(self, text: str) -> Optional[str]:
        """
        텍스트에서 수식 추출
        """
        if not text:
            return None
        
        # 수식 패턴: 변수, 지수, 연산자, 등호 등
        formula_pattern = r'[a-zA-Z]\s*[²³⁴⁵⁶⁷⁸⁹⁰⁺⁻⁼⁽⁾∫∑∏√∞±×÷≤≥≠≈]|[\+\-\*\/\=\<\>\(\)\^]|\\[a-zA-Z]+'
        
        matches = re.finditer(formula_pattern, text)
        if matches:
            # 첫 번째 수식 부분 추출
            match = next(matches, None)
            if match:
                start = match.start()
                # 수식이 끝나는 지점 찾기
                end = start
                for i in range(start, min(start + 50, len(text))):
                    char = text[i]
                    if re.match(r'[.!?]', char) or (i > start + 10 and re.match(r'\s', char)):
                        end = i
                        break
                if end == start:
                    end = min(start + 50, len(text))
                return text[start:end].strip()
        
        return None


