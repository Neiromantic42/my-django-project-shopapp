from django.contrib import admin
from .models import Article

admin.site.register(Article) # Регистрируем модель статьи в админке

