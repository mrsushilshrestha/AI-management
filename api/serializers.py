from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AIModel, Prompt

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        extra_kwargs = {'password': {'write_only': True}}

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ['id', 'name']

class PromptSerializer(serializers.ModelSerializer):
    ai_model_name = serializers.CharField(source='ai_model.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Prompt
        fields = ['id', 'prompt_text', 'response_text', 'ai_model', 'ai_model_name', 'username', 'created_at']
        read_only_fields = ['response_text', 'created_at', 'user']