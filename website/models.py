import json
import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

# 1. Profile моделі (ТЕК БІР РЕТ)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.png', upload_to='avatars/')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.CharField(max_length=255, blank=True, verbose_name="Мекенжай")

    def __str__(self):
        return f'{self.user.username} Профилі'

# 2. Лог жазу функциясы
def log_activity(username, action):
    file_path = os.path.join(settings.BASE_DIR, 'user_activity.json')
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = []
    data.append({
        "username": username,
        "action": action,
        "timestamp": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source": "models_signal"
    })
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 3. Сигнал (ТЕК БІР РЕТ ЖӘНЕ ҚАУІПСІЗ)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # get_or_create қате шығармайды
        Profile.objects.get_or_create(user=instance)
        # JSON лог жазу
        log_activity(instance.username, "register_success")

# 4. Категория
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Мезгіл аты")
    slug = models.SlugField(unique=True, verbose_name="URL сілтемесі")

    def __str__(self):
        return self.name

# 5. Тауар
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200, verbose_name="Тауар аты")
    price = models.IntegerField(verbose_name="Бағасы")
    image = models.ImageField(upload_to='products/', verbose_name="Суреті")
    description = models.TextField(blank=True, verbose_name="Сипаттамасы")

    def __str__(self):
        return self.title

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Пайдаланушыға байлау
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"