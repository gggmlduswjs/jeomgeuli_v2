"""
텍스트 처리 관련 뷰 (압축, 요약 등)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import google.generativeai as genai
from core.decorators import handle_api_errors
from core.exceptions import ValidationException, AIAnalysisException


@csrf_exempt
@handle_api_errors
def compress_text(request):
    """
    텍스트 압축 (언어영역 지문용)
    POST /api/exam/compress/
    Body: { text: string, mode: 'compressed' | 'outline', targetRatio: number }
    """
    if request.method != 'POST':
        raise ValidationException('POST만 지원', user_message='POST 요청만 지원됩니다.')
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValidationException(
            '잘못된 JSON 형식입니다',
            user_message='요청 데이터 형식이 올바르지 않습니다.'
        )
    
    text = data.get('text', '').strip()
    mode = data.get('mode', 'compressed')  # compressed, outline
    target_ratio = data.get('targetRatio', 0.3)  # 30%
    
    if not text:
        raise ValidationException(
            '텍스트가 필요합니다',
            user_message='압축할 텍스트를 입력해주세요.'
        )
    
    if mode not in ['compressed', 'outline']:
        mode = 'compressed'
    
    try:
        # Gemini API 사용
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise AIAnalysisException(
                'AI API 키가 설정되지 않았습니다',
                user_message='AI 서비스 설정이 필요합니다.'
            )
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
다음 수능 언어영역 지문을 {mode} 모드로 압축해주세요.
원문 길이의 {target_ratio * 100}% 수준으로 줄여주세요.

모드별 요구사항:
- compressed: 핵심 문장만 재구성하여 원문의 의미를 유지하되 길이를 줄입니다.
- outline: 줄거리 기반 순서 요약으로 등장인물/사건 중심으로 요약합니다.

원문:
{text}

압축된 텍스트만 반환해주세요. 설명이나 추가 문구 없이 압축된 텍스트만 출력해주세요.
"""
        
        response = model.generate_content(prompt)
        compressed = response.text.strip()
        
        return JsonResponse({
            'compressed_text': compressed,
            'original_length': len(text),
            'compressed_length': len(compressed),
            'compression_ratio': len(compressed) / len(text) if text else 0,
            'mode': mode,
        })
    except Exception as e:
        raise AIAnalysisException(
            f'압축 중 오류: {str(e)}',
            user_message='텍스트 압축 중 오류가 발생했습니다.'
        )


@csrf_exempt
@handle_api_errors
def get_sentence_summary(request):
    """
    문장 요약 (문장 반복 모드용)
    POST /api/exam/sentence-summary/
    Body: { sentence: string }
    """
    if request.method != 'POST':
        raise ValidationException('POST만 지원', user_message='POST 요청만 지원됩니다.')
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValidationException(
            '잘못된 JSON 형식입니다',
            user_message='요청 데이터 형식이 올바르지 않습니다.'
        )
    
    sentence = data.get('sentence', '').strip()
    
    if not sentence:
        raise ValidationException(
            '문장이 필요합니다',
            user_message='요약할 문장을 입력해주세요.'
        )
    
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise AIAnalysisException(
                'AI API 키가 설정되지 않았습니다',
                user_message='AI 서비스 설정이 필요합니다.'
            )
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
다음 문장을 한 문장으로 요약해주세요. 핵심 의미만 간단히 설명해주세요.

문장: {sentence}

요약:
"""
        
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        return JsonResponse({
            'summary': summary,
            'original': sentence,
        })
    except Exception as e:
        raise AIAnalysisException(
            f'요약 중 오류: {str(e)}',
            user_message='문장 요약 중 오류가 발생했습니다.'
        )

