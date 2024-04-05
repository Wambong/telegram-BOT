from django.contrib import admin
from .models import Product, Subscriber, Category, Newsletter
# Register your models here.
admin.site.register(Product)
admin.site.register(Subscriber)
admin.site.register(Category)
admin.site.register(Newsletter)