

import logging
import requests
import tempfile
import os
import telebot
from django.conf import settings
from .models import Product, Category, Subscriber, Newsletter
from telebot import TeleBot
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .forms import NewsletterForm

bot1 = TeleBot(settings.TELEGRAM_BOT_TOKEN)
logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
    }
    response = requests.post(url, data=data)
    logger.debug(response.text)
    return response.json()
def process_telegram_event(event):
    message = event.get('message', {})
    logger.debug("Received message:", message)
    if not message:
        logger.error("Received message is None!")
        return
    text = message.get('text', '').strip()
    chat_id = message.get('chat', {}).get('id')
    user_id = str(message.get('from', {}).get('id'))
    is_admin = user_id in settings.TELEGRAM_BOT_ADMINS
    response_message = None
    if text.startswith('/new'):
        response_message = get_latest_phones(chat_id)
        send_telegram_message(chat_id, response_message)
    elif text.startswith('/start'):
        save_chat_id_to_database(chat_id)
        send_telegram_message(chat_id, 'You are now subscribed to the newsletter!')
    elif text.startswith('/search'):
        query = text.split(' ', 1)[1] if len(text.split(' ', 1)) > 1 else ''
        response_message = search_products(chat_id, query)
        send_telegram_message(chat_id, response_message)
    elif text.startswith('/categories'):
        if is_admin:
            response_message = get_category_list()
        else:
            response_message = "Sorry, you're not authorized to use this command."
        send_telegram_message(chat_id, response_message)
    elif text.startswith('/delete'):
        if is_admin:
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                response_message = "Please specify the product name to delete."
            else:
                product_name = parts[1]
                response_message = delete_product_by_name(chat_id, product_name)
        else:
            response_message = "Sorry, you're not authorized to use this command."
        send_telegram_message(chat_id, response_message)
    elif text.startswith('/add'):
        if is_admin:
            parts = text.split(' ', 1)
            if len(parts) < 2:
                response_message = "Please provide product details in the format: /add product name, description, color, price, category"
            else:
                try:
                    product_data = parts[1].strip().split(",")
                    name = product_data[0].strip()
                    description = product_data[1].strip()
                    color = None
                    if len(product_data) > 2:
                        color = product_data[2].strip()
                    price = float(product_data[3].strip())

                    # Get the category name from the input
                    category_name = product_data[4].strip()

                    # Query the Category model to get the category object
                    category = Category.objects.filter(name=category_name).first()

                    if category:
                        if 'photo' in message:
                            file_id = message['photo'][-1]['file_id']
                            file_path = bot1.get_file(file_id)['file_path']
                            image_url = f'https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}'
                            with requests.get(image_url, stream=True) as r:
                                r.raise_for_status()
                                with tempfile.NamedTemporaryFile(delete=False) as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                    image_path = f.name
                            with open(image_path, 'rb') as image_file:
                                new_product = Product.objects.create(
                                    name=name,
                                    description=description,
                                    color=color,
                                    price=price,
                                    image=image_file
                                )
                            os.unlink(image_path)
                        else:
                            new_product = Product.objects.create(
                                name=name,
                                description=description,
                                color=color,
                                price=price,
                                categories=category  # Assign the category directly to the product
                            )
                            response_message = f"Successfully added product: {name}"
                    else:
                        response_message = f"Category '{category_name}' does not exist."
                except ValueError:
                    response_message = "Invalid product data format. Please see the help message for the /add command."
        else:
            response_message = "Sorry, you're not authorized to use this command."
        send_telegram_message(chat_id, response_message)


def get_latest_phones(chat_id):
    try:
        latest_products = Product.objects.all().order_by('-created_at')[:5]
        if not latest_products.exists():
            return "No latest products found."
        for product in latest_products:
            category = product.categories
            category_name = category.name if category else "Uncategorized"
            text_message = (
                f"Name: {product.name}\n"
                f"Description: {product.description}\n"
                f"Color: {product.color}\n"
                f"Price: {product.price}\n"
                f"Category: {category_name}\n"  # Access category directly
                f"Created At: {product.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            if product.image:
                with open(product.image.path, 'rb') as image_file:
                    bot1.send_photo(chat_id, image_file)
            bot1.send_message(chat_id, text_message)
        return ""
    except Exception as e:
        logger.error("Error in get_latest_phones function:", e)
        return "An error occurred while retrieving latest products."

def search_products(chat_id, query):
    try:
        matching_products = Product.objects.filter(name__icontains=query)
        if not matching_products.exists():
            return "No products found matching your query."

        message_lines = ["Search Results:"]
        for product in matching_products:
            try:
                categories = product.categories.all()  # Attempt to access categories
            except AttributeError as e:
                logger.error(f"Error accessing categories for product {product.id}: {e}")
                categories = []

            text_message = (
                f"Name: {product.name}\n"
                f"Description: {product.description}\n"
                f"Color: {product.color}\n"
                f"Price: {product.price}\n"
                f"Categories: {', '.join(category.name for category in categories)}\n"  # Use categories variable
                f"Created At: {product.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            if product.image:
                with open(product.image.path, 'rb') as image_file:
                    bot1.send_photo(chat_id, image_file)

            bot1.send_message(chat_id, text_message)
        return ""
    except Exception as e:
        logger.error("Error in search_products function:", e)
        return "An error occurred while searching for products."
def get_category_list():
    categories = Category.objects.all()
    if not categories.exists():
        return "No categories found."
    message_lines = ["Available Categories:"]
    for category in categories:
        message_lines.append(f"- {category.name}")

    return "\n".join(message_lines)


def delete_product_by_name(chat_id, product_name):
    if str(chat_id) not in settings.TELEGRAM_BOT_ADMINS:
        return "You do not have permission to delete products."

    matching_products = Product.objects.filter(name__iexact=product_name)

    if not matching_products.exists():
        return "Product not found."

    matching_products.first().delete()


def subscribe(request):
    token = settings.TELEGRAM_BOT_TOKEN
    telegram_login_url = f'https://telegram.me/bot{token}?start'
    return redirect(telegram_login_url)


def save_chat_id_to_database(chat_id):
    if chat_id:
        if not Subscriber.objects.filter(chat_id=chat_id).exists():
            Subscriber.objects.create(chat_id=chat_id)


def create_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST, request.FILES)
        if form.is_valid():
            newsletter = form.save()

            chat_ids = Subscriber.objects.values_list('chat_id', flat=True)

            for chat_id in chat_ids:
                try:
                    if newsletter.image:
                        with open(newsletter.image.path, 'rb') as image_file:
                            bot1.send_photo(chat_id, image_file)
                    send_telegram_message(chat_id, newsletter.content)
                except Exception as e:
                    print(f"Error sending newsletter to chat ID {chat_id}: {e}")

            return redirect('create_newsletter')
    else:
        form = NewsletterForm()
    return render(request, 'create_newsletter.html', {'form': form})
