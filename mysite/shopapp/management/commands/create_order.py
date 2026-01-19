from collections.abc import Sequence                     # Для аннотации типов: последовательность объектов Product
from django.contrib.auth.models import User              # Модель пользователя Django
from django.db import transaction                        # Работа с транзакциями (atomic)
from django.core.management import BaseCommand           # Базовый класс для management-команд
from shopapp.models import Product, Order               # Модели Product и Order из твоего приложения


class Command(BaseCommand):
    """
    Команда для создания заказа.

    Демонстрирует:
    - создание заказа с привязкой к пользователю
    - добавление товаров к заказу
    - использование транзакций для атомарности
    """
    help = "Creates order"                               # Описание команды для manage.py help

    @transaction.atomic                                   # Все действия внутри метода атомарные (ACID)
    def handle(self, *args, **options):
        """
        Основная логика команды.

        - Получение пользователя
        - Получение списка товаров
        - Создание или получение существующего заказа
        - Добавление товаров в заказ
        - Сохранение заказа
        """

        self.stdout.write("Create order with product")  # Логируем начало операции
        user = User.objects.get(username="admin")  # Получаем пользователя с username='admin'
        # Получаем коллекцию товаров и игнорируем только указанные в defer поля! пример оптимизации
        # products: Sequence[Product] = Product.objects.defer("description", "price", "created_at").all()
        # Получаем коллекцию товаров, выбираем только поле id для оптимизации
        products: Sequence[Product] = Product.objects.only("id").all()
        # Создаём заказ или получаем существующий с заданными параметрами
        order, created = Order.objects.get_or_create(
            delivery_address="Ul Tolstoy, d Kolotushkina 8", # Адрес доставки
            promocode="promo2",  # Промокод заказа
            user=user     # Привязка к пользователю
        )
        # order + 1 # Закомментировано: можно раскомментировать для теста отката транзакции
        for product in products: # Перебираем все продукты
            order.products.add(product) # Добавляем каждый товар в ManyToMany поле заказа
        order.save()  # Сохраняем заказ в базе данных
        self.stdout.write(f"Created order {order}")  # Логируем успешное создание заказа