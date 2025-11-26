"""
콘텐츠 추출 유틸리티
수식, 키워드, 핵심 문장 등을 추출
"""
import re
from typing import List


def extract_formula(text: str) -> str:
    """
    수식 추출 (예: "x² + 2x + 1 = 0")
    """
    if not text:
        return ''
    
    # 수식 패턴: 변수, 지수, 연산자, 등호 등
    formula_pattern = r'[a-zA-Z]\s*[²³⁴⁵⁶⁷⁸⁹⁰⁺⁻⁼⁽⁾∫∑∏√∞±×÷≤≥≠≈]|[\+\-\*\/\=\<\>\(\)\^]|\\[a-zA-Z]+'
    
    match = re.search(formula_pattern, text)
    if match:
        # 수식 부분만 추출
        formula_start = match.start()
        # 수식이 끝나는 지점 찾기 (공백, 문장부호 등)
        formula_end = formula_start
        for i in range(formula_start, len(text)):
            char = text[i]
            if re.match(r'[.!?]', char) or (re.match(r'\s', char) and i > formula_start + 10):
                formula_end = i
                break
        if formula_end == formula_start:
            formula_end = min(formula_start + 50, len(text))
        return text[formula_start:formula_end].strip()
    
    return ''


def split_sentences(text: str) -> List[str]:
    """
    텍스트를 문장 단위로 분할
    """
    if not text:
        return []
    
    # 문장 분리 (마침표, 느낌표, 물음표 기준)
    sentences = re.split(r'[.!?]\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def extract_keywords(text: str, max_count: int = 3) -> List[str]:
    """
    핵심 키워드 추출
    """
    if not text:
        return []
    
    # 한글 키워드 패턴 (2글자 이상 명사)
    korean_keyword_pattern = r'[가-힣]{2,}'
    korean_matches = re.findall(korean_keyword_pattern, text)
    
    # 영어 키워드 패턴 (3글자 이상 단어)
    english_keyword_pattern = r'\b[a-zA-Z]{3,}\b'
    english_matches = re.findall(english_keyword_pattern, text)
    
    # 키워드 빈도 계산
    keyword_count = {}
    for keyword in korean_matches + english_matches:
        lower = keyword.lower()
        keyword_count[lower] = keyword_count.get(lower, 0) + 1
    
    # 빈도순으로 정렬
    sorted_keywords = sorted(
        keyword_count.items(),
        key=lambda x: x[1],
        reverse=True
    )[:max_count]
    
    return [keyword for keyword, _ in sorted_keywords]


def contains_formula(text: str) -> bool:
    """
    수식이 포함된 텍스트인지 확인
    """
    if not text:
        return False
    
    formula_pattern = r'[a-zA-Z]\s*[²³⁴⁵⁶⁷⁸⁹⁰⁺⁻⁼⁽⁾∫∑∏√∞±×÷≤≥≠≈]|[\+\-\*\/\=\<\>\(\)\^]|\\[a-zA-Z]+'
    return bool(re.search(formula_pattern, text))

