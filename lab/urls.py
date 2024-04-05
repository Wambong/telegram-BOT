from django.urls import path
from .views import register , registration_success , product_list, product_add, product_edit, product_delete , product_detail 
from . import views
from . import utils

urlpatterns = [
    path('register/', register, name='register'),
    path('registration_success/', registration_success, name='registration_success'),
    path('', product_list, name='product_list'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('add/', product_add, name='product_add'),
    path('edit/<int:pk>/', product_edit, name='product_edit'),
    path('delete/<int:pk>/', product_delete, name='product_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:category_id>/', views.category_products, name='category_products'),
    path('product/search/', views.product_search, name='product_search'),
    path('category/search/', views.category_search, name='category_search'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('add-news/', views.add_news, name='add_news'),
    path('create_newsletter/', utils.create_newsletter, name='create_newsletter'),
    path('subscribe/', utils.subscribe, name='subscribe'),

]
