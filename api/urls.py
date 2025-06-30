from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register_view, login_view, logout_view,
    prompt_form_view, prompt_list_view, dashboard_view, welcome_view
)
from .viewsets import UserViewSet, AIModelViewSet, PromptViewSet

# Create a router for REST API viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'ai-models', AIModelViewSet)
router.register(r'prompts', PromptViewSet, basename='prompt')

urlpatterns = [
    # Original template-based views
    path('', welcome_view, name='welcome'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('submit-prompt/', prompt_form_view, name='prompt_form'),
    path('prompts/', prompt_list_view, name='prompt_list'),
    
    # REST API endpoints
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
