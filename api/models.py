from django.db import models
from django.contrib.auth.models import User

# AIModel stores different AI model names (e.g., GPT-3, BERT, etc.)
class AIModel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Prompt stores the user's prompt and associated response
class Prompt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompts')
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    prompt_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
