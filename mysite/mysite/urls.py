"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings # Доступ к настройкам проекта (settings.py).
from django.conf.urls.static import static # Для раздачи статических и медиа-файлов в режиме разработки.
from django.contrib import admin # Подключение административной панели Django.
from django.urls import path, include # path — для маршрутов; include — для подключения маршрутов из других приложений.
# Специальный помощник для маршрутов с поддержкой разных языков (/en/, /ru/).
# он добавляет префиксы для каждой подключенной ссылки, со значением языка который выбрал пользователь
from django.conf.urls.i18n import i18n_patterns

from drf_spectacular.views import (
    SpectacularAPIView,  # генерирует OpenAPI-схему по вашим View/Serializer/Model
    SpectacularSwaggerView, SpectacularRedocView,  # отображает UI Swagger с использованием сгенерированной схемы
)


from django.contrib.sitemaps.views import sitemap # Встроенное представление Django для генерации sitemap.xml
from .sitemaps import sitemaps # Импортируем словарь с зарегистрированными sitemap

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('article/', include('blogapp.urls')), # Подключаем маршруты приложения blogapp; все URL будут начинаться с /article/
    path('blog/', include('new_blogapp_rss.urls')), # Подключаем маршруты приложения new_blogapp_rss; все URL будут начинаться с /blog/
    path( # URL для карты сайта
        "sitemap.xml",
        sitemap, # sitemap — view, которое генерирует XML
        {"sitemaps": sitemaps}, # sitemaps — передаём описанные sitemap-классы
        name="django.contrib.sitemaps.views.sitemap" # name — имя маршрута для обращения к URL
    )
] # список маршрутов

urlpatterns += i18n_patterns( # Маршруты приложения myauth с поддержкой переключения языка (через /ru/, /en/)
path('admin/', admin.site.urls), # URL для встроенной админки Django; админка доступна по /admin/
    path('accounts/', include('myauth.urls')), # Маршруты авторизации (раньше myauth/, теперь accounts/)
    path('shop/', include('shopapp.urls')), # Подключаем маршруты приложения shopapp; все URL будут начинаться с /shop/
)

urlpatterns += [
    # Эндпоинт для генерации OpenAPI-схемы в формате JSON
    path(
        'api/schema/',                # URL для получения схемы API
        SpectacularAPIView.as_view(),      # Представление, генерирующее JSON-схему
        name='schema'                      # Имя маршрута для использования внутри Django
    ),
    # Swagger UI — визуальная документация на основе OpenAPI-схемы
    path(
        'api/swagger-ui/',            # URL для доступа к Swagger-интерфейсу
        SpectacularSwaggerView.as_view(    # Представление, которое рендерит Swagger UI
            url_name='schema'              # Указываем, откуда брать OpenAPI-схему
        ),
        name='swagger-ui'                  # Имя маршрута для ссылок внутри Django
    ),
    # ReDoc — альтернативная визуальная документация API
    path(
        'api/redoc/',                 # URL для доступа к ReDoc-интерфейсу
        SpectacularRedocView.as_view(      # Представление, которое рендерит ReDoc
            url_name='schema'              # Указываем, откуда брать OpenAPI-схему
        ),
        name='redoc'                        # Имя маршрута для ссылок внутри Django
    ),
]

# Проверяем, включён ли режим разработки
if settings.DEBUG:
    # Если да, добавляем маршруты для отдачи медиа-файлов через встроенный сервер Django
    urlpatterns.extend(
        # static() создаёт временные URL-ы для файлов, лежащих в MEDIA_ROOT
        # settings.MEDIA_URL — URL, по которому будут доступны файлы (например: /media/)
        # document_root=settings.MEDIA_ROOT — реальная папка на диске, где лежат файлы
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

    # Добавляем маршруты для отдачи статических файлов через встроенный сервер Django
    urlpatterns.extend(
        # static() создаёт временные URL-ы для статических файлов
        # settings.STATIC_URL — URL, по которому будут доступны статические файлы (например: /static/)
        # document_root=settings.STATIC_ROOT — реальная папка на диске, где лежат все собранные статические файлы
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )

    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )