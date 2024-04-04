from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Product, Comment
from .utils import send_telegram_message
from django.conf import settings

@receiver(post_save, sender=Product)
def send_product_added_message(sender, instance, created, **kwargs):
    if created:
        message = f'New product added: {instance.name}\nDescription: {instance.description[:100]}\nPrice: ${instance.price}'
        send_telegram_message(settings.DEFAULT_CHAT_ID, message)

@receiver(pre_delete, sender=Product)
def send_product_deleted_message(sender, instance, **kwargs):
    message = f'The product "{instance.name}" has been deleted.'
    send_telegram_message(settings.DEFAULT_CHAT_ID, message)

@receiver(post_save, sender=Comment)
def send_comment_posted_message(sender, instance, created, **kwargs):
    if created:
        message = f'New comment on "{instance.product.name}" by {instance.author}: {instance.text[:100]}'
        send_telegram_message(settings.DEFAULT_CHAT_ID, message)

