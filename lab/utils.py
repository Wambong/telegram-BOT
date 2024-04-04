import requests
import logging
import tempfile
import os
import telebot
from django.conf import settings
from .models import Product, Category
from telebot import TeleBot
bot1 = TeleBot(settings.TELEGRAM_BOT_TOKEN)
from .models import Subscriber
logger = logging.getLogger(__name__)

def send_telegram_message(chat_id, message):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
    }
    response = requests.post(url, data=data)
    logger.debug(response.text)  # Log the API response text
    return response.json()



def process_telegram_event(event):
    message = event.get('message', {})
    text = message.get('text', '').strip()
    chat_id = message.get('chat', {}).get('id')  # Get the chat_id from the incoming message
    user_id = str(message.get('from', {}).get('id'))
    is_admin = user_id in settings.TELEGRAM_BOT_ADMINS

    response_message = None  # Define response_message variable with None value by default

    if text.startswith('/new'):
        response_message = get_latest_phones(chat_id)
        send_telegram_message(chat_id, response_message)

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
            parts = text.split(' ', 1)  # Split command and potentially following data
            if len(parts) < 2:
                response_message = "Please provide product details in the format: /add product name, description, color, price, (category1 category2 ...)"
            else:
                try:
                    product_data = parts[1].strip().split(",")
                    name = product_data[0].strip()
                    description = product_data[1].strip()
                    color = None  # Optional color
                    if len(product_data) > 2:
                        color = product_data[2].strip()
                    price = float(product_data[3].strip())

                    categories = []
                    for category_name in parts[4:]:
                        category = Category.objects.filter(name=category_name.strip())
                        if category.exists():
                            categories.append(category.first())
                        else:
                            response_message = f"Category '{category_name.strip()}' does not exist."
                            break

                    # Check if there's an image attached to the message
                    if 'photo' in message:
                        # Get the file ID of the photo
                        file_id = message['photo'][-1]['file_id']
                        # Get the file path of the photo
                        file_path = bot1.get_file(file_id)['file_path']
                        # Download the photo
                        image_url = f'https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}'
                        with requests.get(image_url, stream=True) as r:
                            r.raise_for_status()
                            # Create a temporary file to store the image
                            with tempfile.NamedTemporaryFile(delete=False) as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                                # Get the path of the temporary file
                                image_path = f.name
                        # Open the temporary file as binary and associate it with the product
                        with open(image_path, 'rb') as image_file:
                            new_product = Product.objects.create(
                                name=name,
                                description=description,
                                color=color,
                                price=price,
                                image=image_file
                            )
                        # Delete the temporary file
                        os.unlink(image_path)
                    else:
                        # If no image is attached, create the product without an image
                        new_product = Product.objects.create(
                            name=name,
                            description=description,
                            color=color,
                            price=price,
                        )
                    # Set categories for the product
                    new_product.categories.set(categories)
                    response_message = f"Successfully added product: {name}"
                except ValueError:
                    response_message = "Invalid product data format. Please see the help message for the /add command."
        else:
            response_message = "Sorry, you're not authorized to use this command."

    send_telegram_message(chat_id, response_message)


# chat_id = '5102556482'


def get_latest_phones(chat_id):
    latest_products = Product.objects.all().order_by('-created_at')[:5]
    if not latest_products.exists():
        return "No latest products found."

    for product in latest_products:
        text_message = (
            f"Name: {product.name}\n"
            f"Description: {product.description}\n"
            f"Color: {product.color}\n"
            f"Price: {product.price}\n"
            f"Categories: {', '.join(category.name for category in product.categories.all())}\n"
            f"Created At: {product.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if product.image:
            with open(product.image.path, 'rb') as image_file:
                # Send the image first
                bot1.send_photo(chat_id, image_file)

        # Then send the text message
        bot1.send_message(chat_id, text_message)

    return ""


def search_products(chat_id, query):
    # Assuming 'name' is a field on your Product model
    matching_products = Product.objects.filter(name__icontains=query)
    if not matching_products.exists():
        return "No products found matching your query."

    message_lines = ["Search Results:"]
    for product in matching_products:
        text_message = (
            f"Name: {product.name}\n"
            f"Description: {product.description}\n"
            f"Color: {product.color}\n"
            f"Price: {product.price}\n"
            f"Categories: {', '.join(category.name for category in product.categories.all())}\n"
            f"Created At: {product.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if product.image:
            with open(product.image.path, 'rb') as image_file:
                # Send the image first
                bot1.send_photo(chat_id, image_file)

        bot1.send_message(chat_id, text_message)


def get_category_list():
    from .models import Category  # Import the Category model
    categories = Category.objects.all()
    if not categories.exists():
        return "No categories found."
    message_lines = ["Available Categories:"]
    for category in categories:
        message_lines.append(f"- {category.name}")

    return "\n".join(message_lines)
def delete_product_by_name(chat_id, product_name):
    from .models import Product

    if str(chat_id) not in settings.TELEGRAM_BOT_ADMINS:
        return "You do not have permission to delete products."


    matching_products = Product.objects.filter(name__iexact=product_name)

    if not matching_products.exists():
        return "Product not found."

    matching_products.first().delete()


from django.http import JsonResponse
from django.shortcuts import redirect
import requests


def subscribe(request):
    # Redirect user to Telegram login page
    telegram_login_url = 'https://telegram.org/auth/login'
    return redirect(telegram_login_url)


def get_chat_id(request):
    if request.method == 'POST':
        # Extract chat ID from the incoming message
        update = request.body.decode('utf-8')
        chat_id = extract_chat_id_from_update(update)

        # Save chat ID to database
        save_chat_id_to_database(chat_id)

        return JsonResponse({'message': 'Chat ID saved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request'})

import json

def extract_chat_id_from_update(update):
    try:
        # Parse the JSON data contained in the update
        update_data = json.loads(update)
        # Extract the chat ID from the update
        chat_id = update_data['message']['chat']['id']
        return chat_id
    except (KeyError, json.JSONDecodeError):
        # Handle the case where the structure of the update is unexpected or invalid
        return None

def save_chat_id_to_database(chat_id):
    # Assuming you have a Subscriber model to save chat IDs
    if chat_id:
        # Check if the chat ID already exists in the database
        if not Subscriber.objects.filter(chat_id=chat_id).exists():
            # If not, save the chat ID to the database
            Subscriber.objects.create(chat_id=chat_id)


