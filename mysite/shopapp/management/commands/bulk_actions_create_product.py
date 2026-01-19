from django.core.management import BaseCommand  # Базовый класс для создания management-команд
from shopapp.models import Product             # Модель Product для работы с товарами
from django.db import transaction               # Модуль для атомарных транзакций


class Command(BaseCommand):
    """
    Демонстрационная команда для массового создания товаров (bulk create).

    - Создаёт несколько объектов Product за одну операцию.
    - Использует транзакцию, чтобы гарантировать целостность данных.
    """
    @transaction.atomic  # Гарантирует, что все операции выполняются атомарно
    def handle(self, *args, **options):
        """
        Основной метод команды.

        1. Определяет список товаров.
        2. Создаёт объекты Product через bulk_create.
        3. Выводит результаты в консоль.
        """
        self.stdout.write("Start demo bulk actions")  # Лог начала выполнения команды

        info = [
            ('Smartphone 1', 199),  # Имя и цена товара
            ('Smartphone 2', 299),
            ('Smartphone 3', 399),
        ]

        # Создаём список объектов Product (не сохраняем ещё в БД)
        products = [
            Product(name=name, price=price)
            for name, price in info
        ]

        # Массовая вставка всех товаров в БД за один запрос
        result = Product.objects.bulk_create(products, batch_size=100, ignore_conflicts=True)

        # Вывод каждого созданного объекта в консоль
        for obj in result:
            print(obj)

        self.stdout.write("Done")  # Лог завершения команды