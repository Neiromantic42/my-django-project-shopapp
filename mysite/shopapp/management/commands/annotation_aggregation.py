from email.policy import default

from django.core.management import BaseCommand  # Базовый класс для создания management-команд Django
from shopapp.models import Product, Order       # Импорт моделей Product и Order
from django.db.models import Avg, Max, Min, Count, Sum  # Агрегатные функции ORM


class Command(BaseCommand):
    """
    Management-команда для демонстрации агрегатных запросов Django ORM.

    Аннотирует каждый заказ:
    - total: сумма цен всех товаров в заказе
    - product_count: количество товаров в заказе
    """

    def handle(self, *args: tuple, **options: dict) -> None:
        """
        Основной метод команды.

        Выполняет аннотацию заказов с суммой и количеством товаров
        и выводит результаты в консоль.
        """
        self.stdout.write("Start demo aggregate+annotation")

        orders = Order.objects.annotate(
            total=Sum("products__price", default=0), # Сумма цен всех товаров в заказе
            product_count=Count("products__pk"),  # Количество товаров в заказе
        )

        for order in orders:  # Проходим по всем заказам
            print(
                f"\nЗаказ №{order.pk}\n"                        # ID заказа
                f"Общее кол-во товаров в заказе: {order.product_count}\n"  # Кол-во товаров
                f"Общая сумма товаров в заказе: {order.total}\n"  # Сумма цен товаров
            )

        self.stdout.write("Done")