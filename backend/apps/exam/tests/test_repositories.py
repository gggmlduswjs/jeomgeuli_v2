"""
Repository Pattern Unit Tests
"""
from django.test import TestCase
from apps.exam.models import Textbook, Unit, Question, ExamSession
from apps.exam.repositories import (
    TextbookRepository, UnitRepository, QuestionRepository, ExamSessionRepository
)


class TextbookRepositoryTest(TestCase):
    """TextbookRepository 테스트"""
    
    def setUp(self):
        self.repo = TextbookRepository()
        self.textbook = Textbook.objects.create(
            title="테스트 교재",
            publisher="테스트 출판사",
            year=2024,
            subject="국어"
        )
    
    def test_get_all(self):
        """모든 교재 조회 테스트"""
        textbooks = self.repo.get_all()
        self.assertGreaterEqual(len(textbooks), 1)
        self.assertIn(self.textbook, textbooks)
    
    def test_get_by_id(self):
        """ID로 교재 조회 테스트"""
        found = self.repo.get_by_id(self.textbook.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, self.textbook.id)
        self.assertEqual(found.title, "테스트 교재")
    
    def test_get_by_id_not_found(self):
        """존재하지 않는 ID 조회 테스트"""
        found = self.repo.get_by_id(99999)
        self.assertIsNone(found)
    
    def test_filter_by_subject(self):
        """과목별 교재 조회 테스트"""
        textbooks = self.repo.filter_by_subject("국어")
        self.assertGreaterEqual(len(textbooks), 1)
        self.assertEqual(textbooks[0].subject, "국어")


class UnitRepositoryTest(TestCase):
    """UnitRepository 테스트"""
    
    def setUp(self):
        self.textbook = Textbook.objects.create(
            title="테스트 교재",
            publisher="테스트 출판사",
            year=2024
        )
        self.unit = Unit.objects.create(
            textbook=self.textbook,
            title="테스트 단원",
            order=1,
            content="테스트 내용"
        )
        self.repo = UnitRepository()
    
    def test_get_by_id(self):
        """ID로 단원 조회 테스트"""
        found = self.repo.get_by_id(self.unit.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, self.unit.id)
        self.assertEqual(found.title, "테스트 단원")
    
    def test_get_by_textbook(self):
        """교재별 단원 조회 테스트"""
        units = self.repo.get_by_textbook(self.textbook.id)
        self.assertGreaterEqual(len(units), 1)
        self.assertIn(self.unit, units)
        self.assertEqual(units[0].order, 1)


class QuestionRepositoryTest(TestCase):
    """QuestionRepository 테스트"""
    
    def setUp(self):
        self.textbook = Textbook.objects.create(title="테스트 교재")
        self.unit = Unit.objects.create(
            textbook=self.textbook,
            title="테스트 단원",
            order=1
        )
        self.question = Question.objects.create(
            unit=self.unit,
            question_text="테스트 문제",
            choice1="선택지1",
            choice2="선택지2",
            choice3="선택지3",
            correct_answer=1,
            difficulty=2
        )
        self.repo = QuestionRepository()
    
    def test_get_by_id(self):
        """ID로 문제 조회 테스트"""
        found = self.repo.get_by_id(self.question.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, self.question.id)
        self.assertEqual(found.question_text, "테스트 문제")
    
    def test_get_by_unit(self):
        """단원별 문제 조회 테스트"""
        questions = self.repo.get_by_unit(self.unit.id)
        self.assertGreaterEqual(len(questions), 1)
        self.assertIn(self.question, questions)


class ExamSessionRepositoryTest(TestCase):
    """ExamSessionRepository 테스트"""
    
    def setUp(self):
        self.repo = ExamSessionRepository()
    
    def test_create(self):
        """시험 세션 생성 테스트"""
        session = self.repo.create(
            total_questions=10,
            status='running',
            current_question_index=0,
            answers={}
        )
        self.assertIsNotNone(session)
        self.assertEqual(session.total_questions, 10)
        self.assertEqual(session.status, 'running')
    
    def test_get_by_id(self):
        """ID로 시험 세션 조회 테스트"""
        session = self.repo.create(
            total_questions=10,
            status='running'
        )
        found = self.repo.get_by_id(session.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, session.id)
    
    def test_update(self):
        """시험 세션 업데이트 테스트"""
        session = self.repo.create(
            total_questions=10,
            status='running',
            current_question_index=0
        )
        
        updated = self.repo.update(
            session,
            current_question_index=5,
            answers={'1': 3, '2': 1}
        )
        
        self.assertEqual(updated.current_question_index, 5)
        self.assertEqual(len(updated.answers), 2)


