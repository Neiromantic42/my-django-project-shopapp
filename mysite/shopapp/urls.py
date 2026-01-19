from django.urls import path, include  # Для маршрутизации URL
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page # Импорт декоратора для кеширования
from rest_framework.routers import DefaultRouter  # Роутер для ViewSet

from .views import (
    ShopIndexView,  # Главная страница магазина
    ProductsListView,  # Просмотр списка всех товаров
    OrderListView,  # Просмотр всех заказов
    ProductDetailsView,  # Просмотр конкретного товара
    OrderDetailView,  # Просмотр конкретного заказа
    store_services,  # Вспомогательные функции магазина
    GroupsListView,  # Просмотр групп пользователей
    ProductCreateView,  # Создание нового товара
    ProductUpdateView,  # Обновление существующего товара
    OrderCreateView,  # Создание нового заказа
    ProductDeleteView,  # Удаление существующего товара
    OrderUpdateView,  # Обновление существующего заказа
    OrderDeleteView,  # Удаление существующего заказа
    ProductsDataExportView,  # Экспорт товаров в JSON
    OrdersDataExport,  # Экспорт заказов в JSON
    ProductViewSet,  # ViewSet для работы с товарами через API
    OrderViewSet,  # ViewSet для работы с заказами через API
    LatestProductsFeed, # Класс для отображения ленты магазина rss
    UserOrdersListView, # Класс представление для отображения списка заказов конкретного юзера
    OrdersUserDataExport, # Класс представление для экспорта данных заказа конкретного юзера
)

app_name = "shopapp"  # Имя приложения для namespace в URL

routers = DefaultRouter()  # Создаем роутер DRF
routers.register("products", ProductViewSet)  # Регистрируем ViewSet по адресу /products/
routers.register("orders", OrderViewSet)  # Регистрируем ViewSet по адресу /orders/

urlpatterns = [
    # path('', cache_page(60 * 3)(ShopIndexView.as_view()), name='shop_index'),  # Главная страница магазина (пример с декоратором для кеширования)
    path('', ShopIndexView.as_view(), name='shop_index'),  # Главная страница магазина
    path("api/", include(routers.urls)),  # Подключение API маршрутов ViewSet через роутер
    path('services/', store_services, name='store_services'),  # Доп. сервисы магазина (функция)
    path('groups/', GroupsListView.as_view(), name='group_list'),  # Список групп пользователей
    path('products/', ProductsListView.as_view(), name='products_list'),  # Список всех товаров
    path('products/latest/feed/', LatestProductsFeed(), name='product-feed'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),  # Создание нового товара
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='products_details'),  # Детали конкретного товара
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),  # Обновление товара
    path('products/<int:pk>/arhived/', ProductDeleteView.as_view(), name='product_delete'), # Удаление (архивирование) товара
    path('products/export/', ProductsDataExportView.as_view(), name='products-export'),  # Экспорт товаров в JSON
    path('orders/', OrderListView.as_view(), name='order_list'),  # Список всех заказов
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),  # Создание нового заказа
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_details'),  # Детали конкретного заказа
    path('orders/update/<int:pk>', OrderUpdateView.as_view(), name='order_update'),  # Обновление заказа
    path('orders/<int:pk>/confirm/', OrderDeleteView.as_view(), name='order_delete'),  # Удаление (подтверждение) заказа
    path('orders/export/', OrdersDataExport.as_view(), name='orders-export'),  # Экспорт заказов в JSON
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', OrdersUserDataExport.as_view(), name='users_orders_export')
]  # Регистрируем все URL маршруты приложения, указываем путь и имя для удобного использования


