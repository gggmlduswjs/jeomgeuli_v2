"""
Service Layer Pattern Implementation for Analytics App
비즈니스 로직 캡슐화
"""
from typing import Dict, Optional
from .repositories import (
    BrailleSpeedLogRepository,
    WrongAnswerPatternRepository,
    TimingLogRepository
)


class AnalyticsService:
    """분석 관련 비즈니스 로직"""
    
    def __init__(
        self,
        speed_repo: BrailleSpeedLogRepository = None,
        wrong_answer_repo: WrongAnswerPatternRepository = None,
        timing_repo: TimingLogRepository = None
    ):
        self.speed_repo = speed_repo or BrailleSpeedLogRepository()
        self.wrong_answer_repo = wrong_answer_repo or WrongAnswerPatternRepository()
        self.timing_repo = timing_repo or TimingLogRepository()
    
    def log_wrong_answer(
        self,
        question_id: int,
        wrong_answer: int,
        correct_answer: int,
        pattern_type: str = 'user_mistake'
    ) -> Dict:
        """오답 패턴 로깅"""
        pattern = self.wrong_answer_repo.create(
            question_id=question_id,
            wrong_answer=wrong_answer,
            correct_answer=correct_answer,
            pattern_type=pattern_type,
        )
        
        return {
            'id': pattern.id,
            'question_id': pattern.question_id,
            'pattern_type': pattern.pattern_type,
        }
    
    def log_braille_speed(
        self,
        pattern_count: int,
        time_seconds: float,
        speed_per_minute: float,
        accuracy: float = None
    ) -> Dict:
        """점자 속도 로깅"""
        log = self.speed_repo.create(
            pattern_count=pattern_count,
            time_seconds=time_seconds,
            speed_per_minute=speed_per_minute,
            accuracy=accuracy,
        )
        
        return {
            'id': log.id,
            'speed_per_minute': log.speed_per_minute,
            'created_at': log.created_at.isoformat(),
        }
    
    def log_timing(
        self,
        exam_type: str,
        subject: str = '',
        allocated_time: int = 0,
        used_time: int = 0,
        remaining_time: int = 0
    ) -> Dict:
        """시간 로깅"""
        log = self.timing_repo.create(
            exam_type=exam_type,
            subject=subject,
            allocated_time=allocated_time,
            used_time=used_time,
            remaining_time=remaining_time,
        )
        
        return {
            'id': log.id,
            'exam_type': log.exam_type,
            'created_at': log.created_at.isoformat(),
        }
    
    def get_average_braille_speed(self, days: int = 7) -> float:
        """최근 N일 평균 점자 속도"""
        return self.speed_repo.get_average_speed(days=days)
    
    def get_common_wrong_patterns(self, limit: int = 10) -> list:
        """자주 발생하는 오답 패턴 조회"""
        return self.wrong_answer_repo.get_common_patterns(limit=limit)


