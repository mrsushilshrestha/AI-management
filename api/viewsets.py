from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import AIModel, Prompt
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    AIModelSerializer, PromptSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No account found with that email'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        user = authenticate(username=user_obj.username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'email': user.email
            })
        return Response({'error': 'Invalid credentials'}, 
                        status=status.HTTP_401_UNAUTHORIZED)

class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PromptViewSet(viewsets.ModelViewSet):
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own prompts
        return Prompt.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Set the user automatically to the current user
        ai_model_id = self.request.data.get('ai_model')
        ai_model = None
        if ai_model_id:
            try:
                ai_model = AIModel.objects.get(id=ai_model_id)
            except AIModel.DoesNotExist:
                pass
        
        # Generate a dummy response (in a real app, this would call an AI service)
        response = "This is a dummy AI response generated by the API."
        
        serializer.save(user=self.request.user, ai_model=ai_model, response_text=response)