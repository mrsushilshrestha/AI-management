from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Prompt, AIModel
from datetime import datetime


from django.db.models import Count
from django.db.models.functions import TruncDate

from .models import AIModel

def welcome_view(request):
    ai_models = AIModel.objects.all()
    return render(request, 'welcome.html', {'ai_models': ai_models})

@login_required
def dashboard_view(request):
    if request.user.is_authenticated:
        prompts = Prompt.objects.filter(user=request.user)
        total_prompts = prompts.count()
        last_prompt = prompts.order_by('-created_at').first()
        # Calculate favorite model safely
        top_model = (
            prompts.values('ai_model__name')
            .annotate(count=Count('ai_model'))
            .order_by('-count')
            .first()
        )
        favorite_model = top_model['ai_model__name'] if top_model else None
    else:
        # If user is anonymous, no prompts or stats
        total_prompts = 0
        last_prompt = None
        favorite_model = None

    return render(request, 'dashboard.html', {
        'total_prompts': total_prompts,
        'last_prompt': last_prompt.created_at if last_prompt else None,
        'favorite_model': favorite_model,
    })



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            # Validation
            errors = {}
            if User.objects.filter(email=email).exists():
                errors['email'] = ["Email already exists."]
                
            if User.objects.filter(username=username).exists():
                errors['username'] = ["Username already exists."]

            if len(password) < 8:
                errors['password'] = ["Password must be at least 8 characters long."]

            if errors:
                return JsonResponse(errors, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({
                'username': user.username,
                'email': user.email,
                'success': True,
                'message': "Registration successful. You can now log in."
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return render(request, 'register.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # Validate input
            errors = {}
            if not email:
                errors['email'] = ["Email is required."]
            if not password:
                errors['password'] = ["Password is required."]
                
            if errors:
                return JsonResponse(errors, status=400)

            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'error': 'No account found with that email.'}, status=404)

            user = authenticate(request, username=user_obj.username, password=password)

            if user:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'username': user.username,
                    'token': 'dummy-token-for-demo',  # In a real app, generate a proper token
                    'message': f"Welcome back, {user.username}!"
                })
            else:
                return JsonResponse({'error': 'Incorrect password.'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('welcome')

@login_required
@csrf_exempt
def prompt_form_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt_text = data.get('prompt_text')
            model_name = data.get('ai_model')

            if not prompt_text:
                return JsonResponse({'error': 'Prompt text is required'}, status=400)

            ai_model = None
            if model_name:
                ai_model, _ = AIModel.objects.get_or_create(name=model_name)

            # (Optional) You can connect this to real AI response generation logic
            response = "This is a dummy AI response."

            prompt = Prompt.objects.create(
                user=request.user,
                prompt_text=prompt_text,
                ai_model=ai_model,
                response_text=response
            )

            return JsonResponse({
                'success': True,
                'prompt_id': prompt.id,
                'message': "Prompt submitted successfully."
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return render(request, 'prompt_form.html')


@login_required
def prompt_list_view(request):
    prompts = Prompt.objects.filter(user=request.user).order_by('-created_at')

    # Optional filtering
    date_filter = request.GET.get('date')
    model_filter = request.GET.get('model')

    if date_filter:
        try:
            prompts = prompts.filter(created_at__date=datetime.strptime(date_filter, "%Y-%m-%d").date())
        except ValueError:
            messages.warning(request, "Invalid date format.")

    if model_filter:
        prompts = prompts.filter(ai_model__name__icontains=model_filter)

    # Handle JSON requests
    if request.headers.get('Content-Type') == 'application/json':
        prompts_data = [{
            'id': prompt.id,
            'prompt_text': prompt.prompt_text,
            'response_text': prompt.response_text,
            'ai_model': prompt.ai_model.name if prompt.ai_model else None,
            'created_at': prompt.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for prompt in prompts]
        return JsonResponse({'prompts': prompts_data})

    return render(request, 'prompt_list.html', {'prompts': prompts})
