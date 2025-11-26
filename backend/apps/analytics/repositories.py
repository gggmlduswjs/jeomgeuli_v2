"""
Repository Pattern Implementation for Analytics App
"""
from typing import List, Optional
from datetime import datetime, timedelta
from .models import BrailleSpeedLog, WrongAnswerPattern, TimingLog


class BrailleSpeedLogRepository:
    """BrailleSpeedLog 데이터 접근"""
    
    def create(self, **kwargs) -> BrailleSpeedLog:
        """새 속도 로그 생성"""
        return BrailleSpeedLog.objects.create(**kwargs)
    
    def get_recent(self, limit: int = 20) -> List[BrailleSpeedLog]:
        """최근 로그 조회"""
        return list(
            BrailleSpeedLog.objects
            .order_by('-created_at')[:limit]
        )
    
    def get_average_speed(self, days: int = 7) -> float:
        """최근 N일 평균 속도"""
        since = datetime.now() - timedelta(days=days)
        logs = BrailleSpeedLog.objects.filter(created_at__gte=since)
        if not logs.exists():
            return 0.0
        return sum(log.speed_per_minute for log in logs) / logs.count()


class WrongAnswerPatternRepository:
    """WrongAnswerPattern 데이터 접근"""
    
    def create(self, **kwargs) -> WrongAnswerPattern:
        """새 오답 패턴 생성"""
        return WrongAnswerPattern.objects.create(**kwargs)
    
    def get_by_question(self, question_id: int) -> List[WrongAnswerPattern]:
        """문제별 오답 패턴 조회"""
        return list(
            WrongAnswerPattern.objects
            .filter(question_id=question_id)
            .order_by('-created_at')
        )
    
    def get_common_patterns(self, limit: int = 10) -> List[WrongAnswerPattern]:
        """자주 발생하는 오답 패턴 조회"""
        from django.db.models import Count
        return list(
            WrongAnswerPattern.objects
            .values('pattern_type', 'wrong_answer', 'correct_answer')
            .annotate(count=Count('id'))
            .order_by('-count')[:limit]
        )


class TimingLogRepository:
    """TimingLog 데이터 접근"""
    
    def create(self, **kwargs) -> TimingLog:
        """새 시간 로그 생성"""
        return TimingLog.objects.create(**kwargs)
    
    def get_recent(self, limit: int = 20) -> List[TimingLog]:
        """최근 로그 조회"""
        return list(
            TimingLog.objects
            .order_by('-created_at')[:limit]
        )
    
    def get_by_exam_type(self, exam_type: str) -> List[TimingLog]:
        """시험 유형별 로그 조회"""
        return list(
            TimingLog.objects
            .filter(exam_type=exam_type)
            .order_by('-created_at')
        )


