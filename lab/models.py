from django.db import models
from django.conf import settings



class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    
    class Meta:
        ordering = ['created_at']  # Default ordering
        
    def __str__(self):
        return self.name
    


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.product}'
    


class Newsletter(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='newsletter_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Newsletter #{self.pk}"


class Subscriber(models.Model):
    chat_id = models.CharField(max_length=255)