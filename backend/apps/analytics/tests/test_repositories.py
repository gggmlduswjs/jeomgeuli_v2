"""
Analytics Repository Unit Tests
"""
from django.test import TestCase
from apps.analytics.models import BrailleSpeedLog, WrongAnswerPattern, TimingLog
from apps.analytics.repositories import (
    BrailleSpeedLogRepository, WrongAnswerPatternRepository, TimingLogRepository
)


class BrailleSpeedLogRepositoryTest(TestCase):
    """BrailleSpeedLogRepository 테스트"""
    
    def setUp(self):
        self.repo = BrailleSpeedLogRepository()
    
    def test_create(self):
        """속도 로그 생성 테스트"""
        log = self.repo.create(
            pattern_count=100,
            time_seconds=60.0,
            speed_per_minute=100.0,
            accuracy=0.95
        )
        self.assertIsNotNone(log)
        self.assertEqual(log.pattern_count, 100)
        self.assertEqual(log.speed_per_minute, 100.0)
    
    def test_get_average_speed(self):
        """평균 속도 조회 테스트"""
        # 로그 생성
        self.repo.create(
            pattern_count=100,
            time_seconds=60.0,
            speed_per_minute=100.0
        )
        self.repo.create(
            pattern_count=120,
            time_seconds=60.0,
            speed_per_minute=120.0
        )
        
        avg_speed = self.repo.get_average_speed(days=7)
        self.assertGreater(avg_speed, 0)
        self.assertLessEqual(avg_speed, 120.0)


class WrongAnswerPatternRepositoryTest(TestCase):
    """WrongAnswerPatternRepository 테스트"""
    
    def setUp(self):
        self.repo = WrongAnswerPatternRepository()
    
    def test_create(self):
        """오답 패턴 생성 테스트"""
        pattern = self.repo.create(
            question_id=1,
            wrong_answer=2,
            correct_answer=1,
            pattern_type='user_mistake'
        )
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.question_id, 1)
        self.assertEqual(pattern.wrong_answer, 2)
        self.assertEqual(pattern.correct_answer, 1)
    
    def test_get_by_question(self):
        """문제별 오답 패턴 조회 테스트"""
        self.repo.create(
            question_id=1,
            wrong_answer=2,
            correct_answer=1
        )
        
        patterns = self.repo.get_by_question(1)
        self.assertGreaterEqual(len(patterns), 1)
        self.assertEqual(patterns[0].question_id, 1)


class TimingLogRepositoryTest(TestCase):
    """TimingLogRepository 테스트"""
    
    def setUp(self):
        self.repo = TimingLogRepository()
    
    def test_create(self):
        """시간 로그 생성 테스트"""
        log = self.repo.create(
            exam_type='수능',
            subject='국어',
            allocated_time=80,
            used_time=75,
            remaining_time=5
        )
        self.assertIsNotNone(log)
        self.assertEqual(log.exam_type, '수능')
        self.assertEqual(log.allocated_time, 80)
        self.assertEqual(log.used_time, 75)
    
    def test_get_by_exam_type(self):
        """시험 유형별 로그 조회 테스트"""
        self.repo.create(
            exam_type='수능',
            subject='국어',
            allocated_time=80,
            used_time=75,
            remaining_time=5
        )
        
        logs = self.repo.get_by_exam_type('수능')
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0].exam_type, '수능')


