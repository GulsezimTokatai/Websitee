from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import os
import json
from django.utils import timezone
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Product, Category
from .forms import ProfileUpdateForm

def index(request):
    return render(request, 'website/index.html')


def product(request):
    return render(request, 'website/product.html')


def lookbook(request):
    return render(request, 'website/lookbook.html')

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'website/profile.html', {'form': form, 'profile': profile})


def quiz(request):
    return render(request, 'website/quiz.html')


def second(request):
    return render(request, 'website/second.html')


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile


def register_view(request):
    error_message = None

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            error_message = "Барлық жолақты толтырыңыз!"

        elif User.objects.filter(email=email).exists():
            error_message = "Бұл пошта бұрыннан тіркелген!"

        else:
            # Email-ден username жасау
            username = email.split('@')[0]

            # Егер мұндай username болса, соңына кездейсоқ сан қосу
            if User.objects.filter(username=username).exists():
                import random
                username = f"{username}{random.randint(1, 999)}"

            try:
                # 1. Пайдаланушыны жасау
                # Осы жерде models.py-дағы СИГНАЛ автоматты түрде Профиль жасайды
                user = User.objects.create_user(username=username, email=email, password=password)

                # 2. Жүйеге кіру
                login(request, user)

                # 3. Басты бетке бағыттау
                return redirect('index')

            except Exception as e:
                error_message = f"Қате орын алды: {e}"

    return render(request, 'website/register.html', {'error': error_message})


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 1. Пошта бойынша қолданушыны іздейміз
        try:
            user_obj = User.objects.get(email=email)
            # 2. Аутентификация (username арқылы)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                # Жүйеге кіруді логқа жазу (міндетті болса қалдырыңыз)
                # save_activity_to_json(user.username, "login_success", 0)
                return redirect('index')
            else:
                # Пароль қате болса
                return render(request, 'website/login.html', {'error': 'Құпия сөз қате!'})

        except User.DoesNotExist:
            # Пошта табылмаса
            return render(request, 'website/login.html', {'error': 'Мұндай пошта тіркелмеген!'})

    return render(request, 'website/login.html')

def save_activity_to_json(username, action, errors=0, status="Success"):
    file_path = os.path.join(settings.BASE_DIR, 'user_activity.json')
    print(f"\n--- DEBUG: ФАЙЛ ЖОЛЫ: {file_path} ---\n")

    entry = {
        "username": username,
        "action": action,
        "timestamp": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        "errors_count": errors,
        "status": status
    }

    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = []

    data.append(entry)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def logout_view(request):
    logout(request)
    return redirect('login')


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    return render(request, 'website/kiimder.html', {
        'category': category,
        'products': products
    })


@csrf_exempt
def ask_bot(request):
    if request.method == "POST":
        user_query = request.POST.get('message', '').lower().strip()
        file_path = os.path.join(settings.BASE_DIR, 'bot_knowledge.json')

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        bot_reply = "Кешіріңіз, мен бұл сұраққа жауап бере алмаймын. Бірақ операторға хабар бере аламын."

        for key in data["responses"]:
            if key in user_query:  # Сөйлем ішінен кілт сөзді іздеу
                bot_reply = data["responses"][key]
                break

        log_entry = {
            "user_question": user_query,
            "bot_answer": bot_reply,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["user_logs"].append(log_entry)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return JsonResponse({"reply": bot_reply})


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        size = request.POST.get('size', 'M')  # HTML-ден таңдалған өлшемді алады
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})
        cart_key = f"{product_id}_{size}"  # Ерекше кілт жасау

        if cart_key in cart:
            cart[cart_key]['quantity'] += quantity
        else:
            cart[cart_key] = {
                'product_id': product_id,
                'title': product.title,
                'price': str(product.price),
                'image': product.image.url,
                'size': size,  # Өлшем осы жерде сақталады
                'quantity': quantity,
            }

        request.session['cart'] = cart
        return JsonResponse({'total_items': len(cart)})


def update_cart(request, cart_key):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        new_qty = request.POST.get('quantity')
        new_size = request.POST.get('size')  # Жаңа өлшемді аламыз

        if cart_key in cart:
            # 1. Егер сан өзгерсе
            if new_qty:
                cart[cart_key]['quantity'] = int(new_qty)

            # 2. Егер өлшем өзгерсе (ЕҢ МАҢЫЗДЫ ЖЕРІ ОСЫ)
            if new_size:
                cart[cart_key]['size'] = new_size

            # Сессияны сақтаймыз
            request.session.modified = True
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def cart_detail(request):
    cart = request.session.get('cart', {})
    total_price = 0
    total_items = 0  # Жалпы штук санын сақтау үшін

    for key, item in cart.items():
        price = float(item.get('price', 0))
        quantity = int(item.get('quantity', 1))

        total_price += price * quantity
        total_items += quantity  # Әр тауардың санын қосып отырамыз (мысалы: 1+1+2+...)

    return render(request, 'website/cart.html', {
        'cart': cart,
        'total_price': total_price,
        'total_items': total_items  # Осыны шаблонға жібереміз
    })


def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    if item_id in cart:
        del cart[item_id]
        request.session.modified = True

    return redirect('cart_detail')



def search_view(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    products = Product.objects.filter(title__icontains=query)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    return render(request, 'website/search_result.html', {
        'products': products,
        'query': query,
        'min_price': min_price,
        'max_price': max_price
    })


import google.generativeai as genai
from django.http import JsonResponse
import logging

# Настройка логирования для отслеживания ошибок в консоли
logger = logging.getLogger(__name__)

# Рекомендуется выносить ключ в settings.py или .env файл
API_KEY = "AIzaSyAJjTse0SSxinY7p-Op92LDr-CShSIM7gM"
genai.configure(api_key=API_KEY)


def chat_with_stylist(request):
    user_message = request.GET.get('message')

    if not user_message:
        return JsonResponse({'reply': "Сұрақ жазылмады."}, status=400)

    try:
        # 1. Автоматический подбор лучшей доступной модели
        model_list = genai.list_models()
        available_models = [m.name for m in model_list if 'generateContent' in m.supported_generation_methods]

        # Приоритет отдаем 1.5-flash как самой быстрой, если нет — берем первую из списка
        selected_model_name = next((m for m in available_models if "gemini-1.5-flash" in m), None)
        if not selected_model_name:
            selected_model_name = available_models[0] if available_models else "gemini-pro"

        # 2. Инициализация модели с системной инструкцией
        model = genai.GenerativeModel(
            model_name=selected_model_name,
            system_instruction="Сен — кәсіби стилистсің. Жауаптарыңды тек қазақ тілінде жаз. "
            "Өте қысқа, нақты және нұсқа жауап бер (макс. 3-4 сөйлем немесе 40 сөз). "
            "Артық кіріспе сөздерсіз, бірден кеңеске көш. "
            "Пайдаланушыға киім түстері мен күтім туралы нақты ұсыныс айт."
        )

        # 3. Генерация контента
        response = model.generate_content(user_message)

        if response and response.text:
            return JsonResponse({'reply': response.text})
        else:
            return JsonResponse({'reply': "AI жауап бере алмады, қайта сұрап көріңіз."})

    except Exception as e:
        # Выводит детальную ошибку в терминал Django
        print(f"--- ОШИБКА GEMINI API ---: {str(e)}")
        logger.error(f"Gemini Error: {e}")

        return JsonResponse({
            'reply': "Байланыс орнату мүмкін болмады. Қайта көріңіз.",
            'details': str(e)  # Можно убрать на продакшне
        })