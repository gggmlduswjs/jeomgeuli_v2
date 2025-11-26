from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import ExploreService


@csrf_exempt
def get_news(request):
    """뉴스/시사 요약 조회"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET만 지원'}, status=405)
    
    try:
        query = request.GET.get('query', '오늘의 주요 뉴스')
        
        # ExploreService를 사용하여 뉴스 요약 조회
        service = ExploreService()
        news_result = service.get_news_summary(query)
        sisa_words = service.get_sisa_words(limit=10)
        
        return JsonResponse({
            'ok': True,
            'news': news_result.get('cards', []),
            'summary': news_result.get('summary', ''),
            'simple': news_result.get('simple', ''),
            'keywords': news_result.get('keywords', []),
            'sisa': sisa_words,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

