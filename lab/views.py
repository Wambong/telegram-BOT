from django.shortcuts import render, redirect , get_object_or_404
from .forms import RegistrationForm , ProductForm , CommentForm , CategoryForm , SearchForm, ProductEditForm
from .models import Product , Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.contrib import messages
from .decorators import superuser_required 
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .utils import process_telegram_event
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import logging
from django.views.decorators.csrf import ensure_csrf_cookie

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
          
            return redirect('registration_success')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def registration_success(request):
    return render(request, 'registration_success.html')



def product_list(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        product_list = Product.objects.all().order_by('created_at')  # Order by 'created_at' as an example
        paginator = Paginator(product_list, 8)  

        page_number = request.GET.get('page')
        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            products = paginator.page(paginator.num_pages)

        return render(request, 'product_list.html', {'products': products})
    else:
        # Redirect to login page with a message
        messages.warning(request, 'You need to log in to access this page.')
        return redirect('login')  


def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

def product_edit(request, pk=None):
    if pk:
        product = get_object_or_404(Product, pk=pk)
    else:
        product = None

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_edit.html', {'form': form})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = product.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = CommentForm()
    return render(request, 'product_detail.html', {
        'product': product,
        'comments': comments,
        'form': form
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

@superuser_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})

@superuser_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})

def category_products(request, category_id):
    category = Category.objects.get(pk=category_id)
    products = category.product_set.all()
    return render(request, 'category_products.html', {'category': category, 'products': products})

def product_search(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Filter products based on the search query, excluding existing products
            products = Product.objects.filter(name__icontains=query)
        else:
            products = []
    else:
        products = []
        form = SearchForm()
    
    return render(request, 'product_search_results.html', {'products': products, 'form': form})

def category_search(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            categories = Category.objects.filter(name__icontains=query)
        else:
            categories = []
            form = SearchForm()
 
    
    return render(request, 'category_search_results.html', {'categories': categories, 'form': form})

def category_detail(request, category_id):
    # Retrieve the category object based on category_id
    category = Category.objects.get(pk=category_id)
    # You can customize this view to render the details of the category
    return HttpResponse(f"Category Detail: {category.name}")


logger = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    try:
        update = json.loads(request.body.decode('utf-8'))
        process_telegram_event(update)
        return JsonResponse({'ok': True})
    except Exception as e:
        logger.error(f"Error processing telegram event: {e}")
        return JsonResponse({'ok': False}, status=400)


from .forms import NewsletterForm

def add_news(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_news')
    else:
        form = NewsletterForm()
    return render(request, 'add_news.html', {'form': form})
