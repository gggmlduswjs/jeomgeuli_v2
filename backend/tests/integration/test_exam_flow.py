"""
Integration Tests - Exam Flow
시험 관련 전체 플로우 테스트
"""
from django.test import TestCase, Client
from django.urls import reverse
import json
from apps.exam.models import Textbook, Unit, Question


class ExamFlowIntegrationTest(TestCase):
    """시험 플로우 통합 테스트"""
    
    def setUp(self):
        self.client = Client()
        
        # 테스트 데이터 생성
        self.textbook = Textbook.objects.create(
            title="테스트 교재",
            publisher="테스트 출판사",
            year=2024,
            subject="국어"
        )
        
        self.unit = Unit.objects.create(
            textbook=self.textbook,
            title="테스트 단원",
            order=1,
            content="테스트 내용"
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
    
    def test_textbook_list_flow(self):
        """교재 목록 조회 플로우"""
        response = self.client.get('/api/exam/textbook/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('textbooks', data)
        self.assertGreaterEqual(len(data['textbooks']), 1)
    
    def test_unit_list_flow(self):
        """단원 목록 조회 플로우"""
        response = self.client.get(f'/api/exam/unit/?textbook_id={self.textbook.id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('units', data)
        self.assertGreaterEqual(len(data['units']), 1)
    
    def test_question_submit_flow(self):
        """문제 조회 및 답안 제출 플로우"""
        # 1. 문제 조회
        response = self.client.get(f'/api/exam/question/{self.question.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('question', data)
        self.assertEqual(data['question']['id'], self.question.id)
        
        # 2. 답안 제출
        response = self.client.post(
            '/api/exam/submit/',
            json.dumps({
                'question_id': self.question.id,
                'answer': 1,
                'response_time': 5.0
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('result', data)
        self.assertTrue(data['result']['is_correct'])
    
    def test_exam_session_flow(self):
        """시험 세션 플로우"""
        # 1. 시험 시작
        response = self.client.post(
            '/api/exam/start/',
            json.dumps({
                'total_questions': 10
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('exam_id', data)
        exam_id = data['exam_id']
        
        # 2. 답안 업데이트 (시험 세션 서비스를 통해)
        from apps.exam.services import ExamSessionService
        service = ExamSessionService()
        result = service.update_answer(exam_id, question_id=1, answer=3)
        self.assertIn('answers', result)
        
        # 3. 시험 종료
        result = service.finish_exam(exam_id)
        self.assertEqual(result['status'], 'finished')


