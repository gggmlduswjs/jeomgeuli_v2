"""
텍스트 추출 유틸리티
교재 정보 추출, 단원 추출 등
"""
import re
from typing import Dict, List, Optional


def extract_textbook_info(filename: str) -> dict:
    """
    파일명에서 교재 정보 추출
    예: "수능특강_국어_2024.pdf" → {title: "수능특강 국어", subject: "국어", year: 2024}
    """
    # 확장자 제거
    name = filename.replace('.pdf', '').replace('.PDF', '')
    
    # 패턴 매칭
    patterns = [
        r'(.+?)_(\w+)_(\d{4})',  # 수능특강_국어_2024
        r'(.+?)\s+(\w+)\s+(\d{4})',  # 수능특강 국어 2024
        r'(.+?)_(\d{4})',  # 수능특강_2024
        r'(.+?)\s+(\d{4})',  # 수능특강 2024
    ]
    
    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            if len(match.groups()) == 3:
                title, subject, year = match.groups()
                return {
                    'title': f"{title} {subject}",
                    'subject': subject,
                    'year': int(year),
                    'publisher': 'EBS'  # 기본값
                }
            elif len(match.groups()) == 2:
                title, year = match.groups()
                # year가 숫자인지 확인
                if year.isdigit():
                    return {
                        'title': title,
                        'subject': '',
                        'year': int(year),
                        'publisher': 'EBS'
                    }
                else:
                    # year가 과목일 수도 있음
                    return {
                        'title': f"{title} {year}",
                        'subject': year,
                        'year': None,
                        'publisher': 'EBS'
                    }
    
    # 매칭 실패 시 파일명을 그대로 사용
    return {
        'title': name,
        'subject': '',
        'year': None,
        'publisher': 'EBS'
    }


def extract_units_from_text(text: str, ai_client=None) -> list:
    """
    텍스트에서 단원 정보 추출 (간단한 패턴 매칭)
    
    Args:
        text: 추출할 텍스트
        ai_client: AI 클라이언트 (선택적, 향후 AI 모드 지원용)
    
    Returns:
        [
            {
                'order': 1,
                'title': '1단원',
                'content': '단원 내용...'
            },
            ...
        ]
    """
    units = []
    
    # 간단한 패턴 매칭: "1단원", "제1장", "Chapter 1" 등
    unit_patterns = [
        r'(\d+)단원[:\s]+(.+?)(?=\d+단원|$|제\d+장|Chapter\s+\d+)',
        r'제(\d+)장[:\s]+(.+?)(?=제\d+장|$|\d+단원|Chapter\s+\d+)',
        r'Chapter\s+(\d+)[:\s]+(.+?)(?=Chapter\s+\d+|$|\d+단원|제\d+장)',
        r'제(\d+)과[:\s]+(.+?)(?=제\d+과|$|\d+단원)',
    ]
    
    for pattern in unit_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            order = int(match.group(1))
            content = match.group(2).strip()[:2000]  # 최대 2000자
            if content and len(content) > 50:  # 최소 50자 이상
                units.append({
                    'order': order,
                    'title': f"{order}단원",
                    'content': content
                })
    
    # 중복 제거 (order 기준)
    seen_orders = set()
    unique_units = []
    for unit in units:
        if unit['order'] not in seen_orders:
            seen_orders.add(unit['order'])
            unique_units.append(unit)
    units = sorted(unique_units, key=lambda x: x['order'])
    
    return units

