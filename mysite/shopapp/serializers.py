from rest_framework import serializers  # Импортируем модуль сериализаторов DRF

from .models import Product, Order  # Импортируем модель Product из текущего приложения


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.
    Преобразует объекты Product <-> JSON.
    Используется для чтения, создания, обновления и удаления товаров
    """
    class Meta:  # Класс конфигурации сериализатора
        model = Product  # Указываем, с какой моделью работает сериализатор
        fields = [  # Перечисляем поля, которые попадут в JSON
            "pk",  # Первичный ключ (ID объекта)
            "name",  # Название товара
            "description",  # Описание товара
            "price",  # Цена товара
            "discount",  # Скидка на товар
            "created_at",  # Дата создания объекта
            "archived",  # Флаг, показывающий архивирован товар или нет
            "preview",  # Изображение/обложка товара
        ]


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Order.
    Преобразует объекты Order <-> JSON.
    Используется для чтения, создания, обновления и удаления заказов.
    """
    class Meta:
        model = Order  # Модель, с которой работает сериализатор
        fields = [     # Поля модели Order, которые попадут в JSON-ответ
            "pk", # Первичный ключ заказа
            "delivery_address", # Адрес доставки
            "promocode", # Промокод, если использовался
            "created_at", # Дата и время создания заказа
            "user", # Пользователь, создавший заказ
            "products", # Список товаров в заказе
            "receipt",   # Чек (файл)
        ]