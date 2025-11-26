"""
Vocab Service Unit Tests
"""
from django.test import TestCase
from datetime import date
from apps.vocab.models import Vocabulary, VocabQueue, SisaWord
from apps.vocab.services import VocabLearningService, SisaWordService


class VocabLearningServiceTest(TestCase):
    """VocabLearningService 테스트"""
    
    def setUp(self):
        self.service = VocabLearningService()
        self.vocab = Vocabulary.objects.create(
            word='테스트',
            meaning='테스트 의미',
            example='테스트 예문'
        )
        self.today = date.today()
        self.queue = VocabQueue.objects.create(
            vocab=self.vocab,
            date=self.today,
            order=1
        )
    
    def test_get_today_vocab(self):
        """오늘의 어휘 조회 테스트"""
        vocab_list = self.service.get_today_vocab(self.today)
        self.assertGreaterEqual(len(vocab_list), 1)
        self.assertEqual(vocab_list[0]['word'], '테스트')
        self.assertEqual(vocab_list[0]['queue_id'], self.queue.id)
    
    def test_mark_learned(self):
        """학습 완료 표시 테스트"""
        success = self.service.mark_learned(self.queue.id, grade=3)
        self.assertTrue(success)
        
        # 큐 항목이 학습 완료로 표시되었는지 확인
        self.queue.refresh_from_db()
        self.assertTrue(self.queue.is_learned)


class SisaWordServiceTest(TestCase):
    """SisaWordService 테스트"""
    
    def setUp(self):
        self.service = SisaWordService()
        self.sisa = SisaWord.objects.create(
            word='디플레이션',
            meaning='물가가 지속적으로 하락하는 현상',
            context='경기 침체로 인한 디플레이션 우려',
            source='경제 용어'
        )
    
    def test_get_today_sisa(self):
        """오늘의 시사 용어 조회 테스트"""
        sisa_list = self.service.get_today_sisa(date.today())
        self.assertGreaterEqual(len(sisa_list), 1)
        self.assertEqual(sisa_list[0]['word'], '디플레이션')
    
    def test_get_recent_sisa(self):
        """최근 시사 용어 조회 테스트"""
        sisa_list = self.service.get_recent_sisa(limit=10)
        self.assertGreaterEqual(len(sisa_list), 1)


