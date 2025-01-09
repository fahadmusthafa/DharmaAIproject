from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from .models import Chat
from decouple import config
from django.contrib.auth.decorators import login_required


# Load the API key from environment variables
PERPLEXITY_API_KEY = config('PERPLEXITY_API_KEY')

import requests
from decouple import config

# Load the API key from environment variables
PERPLEXITY_API_KEY = config('PERPLEXITY_API_KEY')

import requests
from decouple import config

# Load the API key from environment variables
PERPLEXITY_API_KEY = config('PERPLEXITY_API_KEY')

# Available models
MODELS = {
    "small": "llama-3.1-sonar-small-128k-online",  # 8B parameters
    "large": "llama-3.1-sonar-large-128k-online",  # 70B parameters
    "huge": "llama-3.1-sonar-huge-128k-online"    # 405B parameters
}

def ask_perplexity(message, model_choice="large"):
    try:
        # Ensure the model choice is valid
        if model_choice not in MODELS:
            raise ValueError("Invalid model choice. Available models: small, large, huge.")
        
        # URL for the Perplexity chat completion API (ensure it’s the correct one for your model)
        url = "https://api.perplexity.ai/chat/completions"

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        # Prepare the request data with the selected model
        data = {
            "model": MODELS[model_choice],  # Use the selected model (small, large, or huge)
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ]
        }

        # Make the POST request to Perplexity API
        response = requests.post(url, json=data, headers=headers)
        
        # Handle the response and extract the message
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            # Log the error message for debugging
            print(f"API Error: {response.status_code} - {response.text}")
            return "Sorry, something went wrong with the Perplexity API."

    except ValueError as e:
        return str(e)  # Invalid model choice
    except Exception as e:
        # Catch other errors (e.g., network issues, etc.)
        return f"An error occurred: {e}"



def chatbot(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Rate limiting
        user_key = f"chatbot_rate_limit_{request.user.id}"
        if cache.get(user_key):
            return JsonResponse({'error': 'Too many requests, please wait a while.'}, status=429)
        cache.set(user_key, True, timeout=10)

        # Get response from Perplexity AI
        response = ask_perplexity(message)

        # Save the chat message and response
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        
        return JsonResponse({'message': message, 'response': response})
    
    return render(request, 'chatbot.html', {'chats': chats})



def chatbot1(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Rate limiting
        user_key = f"chatbot_rate_limit_{request.user.id}"
        if cache.get(user_key):
            return JsonResponse({'error': 'Too many requests, please wait a while.'}, status=429)
        cache.set(user_key, True, timeout=10)

        # Get response from Perplexity AI
        response = ask_perplexity(message)

        # Save the chat message and response
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        
        return JsonResponse({'message': message, 'response': response})
    
    # Pass username to the template
    return render(request, 'chatbot1.html', {'chats': chats, 'username': request.user.username})





def introduction(request):
    return render(request,'introduction.html')

def dashbord(request):
    user=User.objects.all()
    return render(request,'dashbord.html',{'user':user})

@login_required
def chathistory(request):
    # Filter chat objects for the logged-in user
    chat = Chat.objects.filter(user=request.user)
    return render(request, 'chathistory.html', {'chat': chat})


@login_required
def settings(request):
    return render(request,'settings.html')


def login(request):
    if request.user.is_authenticated:
        # Redirect admins and non-admins appropriately
        if request.user.is_staff:  # Admin check
            return redirect('chatbot')  # Change 'admin_chatbot' as needed
        return redirect('chatbot1')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        
        if user:
            auth.login(request, user)
            # Redirect admins and non-admins appropriately
            if user.is_staff:  # Admin check
                return redirect('chatbot')  # Change 'admin_chatbot' as needed
            return redirect('chatbot1')
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'user_login1.html', {'error_message': error_message})
    
    return render(request, 'user_login1.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('user_login')
 
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return render(request, 'registration.html', {'error_message': 'Passwords do not match.'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'registration.html', {'error_message': 'Username already taken.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'registration.html', {'error_message': 'Email already in use.'})
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            # auth.login(request, user)
            return redirect('user_login')
        except Exception as e:
            return render(request, 'registration.html', {'error_message': f'Error creating account: {str(e)}'})
    
    return render(request, 'registration.html')

def logout(request):
    auth.logout(request)
    return redirect('user_login')
