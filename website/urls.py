from django.urls import path
from . import views
from.urls import path

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),
    path('home/', views.index, name='index'),
    path('product/', views.product, name='product'),
    path('lookbook/', views.lookbook, name='lookbook'),
    path('quiz/', views.quiz, name='quiz'),
    path('help/', views.second, name='second'),
    path('logout/', views.logout_view, name='logout'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<str:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<str:cart_key>/', views.update_cart, name='update_cart'),
    path('search/', views.search_view, name='search_result'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat-api/', views.chat_with_stylist, name='chat_with_stylist'),
    path('chat_with_stylist/', views.chat_with_stylist, name='chat_with_stylist'),
]