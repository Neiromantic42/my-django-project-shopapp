from django.core.management import BaseCommand  # Базовый класс для management-команд Django
from shopapp.models import Product              # Модель Product
from django.db.models import Avg, Max, Min, Count  # Агрегатные функции ORM


class Command(BaseCommand):
    """
    Management-команда для демонстрации агрегатных запросов Django ORM.

    Выполняет фильтрацию продуктов по названию и считает:
    - среднюю цену
    - максимальную цену
    - минимальную цену
    - общее количество записей
    """

    def handle(self, *args: tuple, **options: dict) -> None:
        """
        Точка входа management-команды.

        Выполняет агрегатный SQL-запрос к таблице продуктов
        и выводит результат в консоль.
        """
        self.stdout.write("Start demo aggregate")  # Сообщение о начале выполнения команды

        result = (
            Product.objects                      # QuerySet модели Product
            .filter(                             # Фильтрация записей
                name__contains="Smartphone"      # WHERE name LIKE '%Smartphone%'
            )
            .aggregate(                          # Агрегация по всей выборке
                average_price=Avg("price"),      # Средняя цена
                max_price=Max("price"),          # Максимальная цена
                min_price=Min("price"),          # Минимальная цена
                total_quantity=Count("id"),      # Количество записей
            )
        )

        print(result)                             # Вывод словаря с результатами агрегации
        self.stdout.write("Done")                 # Сообщение о завершении команды