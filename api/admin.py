from django.contrib import admin

from .models import AIModel,Prompt

# Register your models here.
admin.site.register(AIModel)
admin.site.register(Prompt)