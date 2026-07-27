from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('ai/', views.ai_chat, name='ai_chat'),
    path('ai/query/', views.ai_query_api, name='ai_query.api'),
    # We'll add CRUD URLs later
]