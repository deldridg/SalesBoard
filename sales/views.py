from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services.ai_query import AIQueryService

# ai_service = AIQueryService()
_ai_service = None

def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIQueryService()
    return _ai_service

SUGGESTED_QUERIES = [
    {"label": "NSW Sales Last Year",  "question": "What were total sales in NSW last year?"},
    {"label": "Top Products",         "question": "Top 5 best selling products"},
    {"label": "Top Salesperson",      "question": "Which salesperson had the highest revenue?"},
    {"label": "Sales of Hardware By Region",            "question": "Hardware Sales performance by region"},
]

def ai_chat(request):
    return render(request, 'sales/ai_chat.html', {"suggested_queries": SUGGESTED_QUERIES})

@csrf_exempt
def ai_query_api(request):
    """API endpoint for chat interactions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            provider = data.get('provider', 'openai')
            mode = data.get('mode', 'query')  # 'query' or 'insights'

            if not question:
                return JsonResponse({'error': 'No question provided'}, status=400)

            if mode == 'insights':
                result = get_ai_service().insights(topic=question, provider=provider)
            else:
                result = get_ai_service().query(question=question, provider=provider)

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)