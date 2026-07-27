import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salesboard.settings')
django.setup()

from sales.services.ai_query import AIQueryService

service = AIQueryService()

result = service.query("What are the top 5 best selling products last year?", provider="openai")
print(result.get("sql"))
print(result.get("success"))