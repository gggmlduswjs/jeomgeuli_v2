"""
Service Layer Unit Tests
"""
from django.test import TestCase
from apps.exam.models import Textbook, Unit, Question
from apps.exam.services import (
    TextbookService, UnitService, QuestionService, ExamSessionService
)


class TextbookServiceTest(TestCase):
    """TextbookService 테스트"""
    
    def setUp(self):
        self.service = TextbookService()
        self.textbook = Textbook.objects.create(
            title="테스트 교재",
            publisher="테스트 출판사",
            year=2024,
            subject="국어"
        )
    
    def test_list_textbooks(self):
        """교재 목록 조회 테스트"""
        textbooks = self.service.list_textbooks()
        self.assertGreaterEqual(len(textbooks), 1)
    
    def test_list_textbooks_by_subject(self):
        """과목별 교재 목록 조회 테스트"""
        textbooks = self.service.list_textbooks(subject="국어")
        self.assertGreaterEqual(len(textbooks), 1)
        self.assertEqual(textbooks[0].subject, "국어")
    
    def test_get_textbook(self):
        """교재 상세 조회 테스트"""
        result = self.service.get_textbook(self.textbook.id)
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], self.textbook.id)
        self.assertEqual(result['title'], "테스트 교재")


class UnitServiceTest(TestCase):
    """UnitService 테스트"""
    
    def setUp(self):
        self.textbook = Textbook.objects.create(title="테스트 교재")
        self.unit = Unit.objects.create(
            textbook=self.textbook,
            title="테스트 단원",
            order=1,
            content="테스트 내용"
        )
        self.service = UnitService()
    
    def test_get_unit(self):
        """단원 상세 조회 테스트"""
        result = self.service.get_unit(self.unit.id)
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], self.unit.id)
        self.assertEqual(result['title'], "테스트 단원")
        self.assertEqual(result['content'], "테스트 내용")
    
    def test_list_units(self):
        """교재별 단원 목록 조회 테스트"""
        units = self.service.list_units(self.textbook.id)
        self.assertGreaterEqual(len(units), 1)
        self.assertEqual(units[0]['id'], self.unit.id)


class QuestionServiceTest(TestCase):
    """QuestionService 테스트"""
    
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
            explanation="해설",
            difficulty=2
        )
        self.service = QuestionService()
    
    def test_get_question(self):
        """문제 상세 조회 테스트"""
        result = self.service.get_question(self.question.id)
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], self.question.id)
        self.assertEqual(result['question_text'], "테스트 문제")
    
    def test_submit_answer_correct(self):
        """정답 제출 테스트"""
        result = self.service.submit_answer(
            question_id=self.question.id,
            user_answer=1,
            response_time=5.0
        )
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['correct_answer'], 1)
    
    def test_submit_answer_wrong(self):
        """오답 제출 테스트"""
        result = self.service.submit_answer(
            question_id=self.question.id,
            user_answer=2,
            response_time=5.0
        )
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['correct_answer'], 1)


class ExamSessionServiceTest(TestCase):
    """ExamSessionService 테스트"""
    
    def setUp(self):
        self.service = ExamSessionService()
    
    def test_start_exam(self):
        """시험 시작 테스트"""
        result = self.service.start_exam(total_questions=10)
        self.assertIsNotNone(result)
        self.assertIn('exam_id', result)
        self.assertEqual(result['total_questions'], 10)
        self.assertEqual(result['status'], 'running')
    
    def test_get_exam_session(self):
        """시험 세션 조회 테스트"""
        start_result = self.service.start_exam(total_questions=10)
        exam_id = start_result['exam_id']
        
        session = self.service.get_exam_session(exam_id)
        self.assertIsNotNone(session)
        self.assertEqual(session['exam_id'], exam_id)
        self.assertEqual(session['total_questions'], 10)
    
    def test_update_answer(self):
        """답안 업데이트 테스트"""
        start_result = self.service.start_exam(total_questions=10)
        exam_id = start_result['exam_id']
        
        result = self.service.update_answer(exam_id, question_id=1, answer=3)
        self.assertIn('answers', result)
        self.assertEqual(result['answers']['1'], 3)
    
    def test_pause_and_resume_exam(self):
        """시험 일시정지 및 재개 테스트"""
        start_result = self.service.start_exam(total_questions=10)
        exam_id = start_result['exam_id']
        
        # 일시정지
        pause_result = self.service.pause_exam(exam_id)
        self.assertEqual(pause_result['status'], 'paused')
        
        # 재개
        resume_result = self.service.resume_exam(exam_id)
        self.assertEqual(resume_result['status'], 'running')
    
    def test_finish_exam(self):
        """시험 종료 테스트"""
        start_result = self.service.start_exam(total_questions=10)
        exam_id = start_result['exam_id']
        
        result = self.service.finish_exam(exam_id)
        self.assertEqual(result['status'], 'finished')
        self.assertIsNotNone(result['ended_at'])


