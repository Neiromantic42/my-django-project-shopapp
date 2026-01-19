from django.core.management import BaseCommand  # Базовый класс для создания management-команд
from shopapp.models import Product             # Модель Product для работы с товарами
from django.db import transaction               # Модуль для атомарных транзакций


class Command(BaseCommand):
    """
    Команда для массового обновления скидки товаров.

    - Обновляет поле discount для всех продуктов, имя которых содержит "Smartphone".
    - Использует транзакцию, чтобы изменения были атомарными.
    """
    @transaction.atomic  # Все операции внутри метода выполняются атомарно
    def handle(self, *args, **options):
        """
        Основной метод команды.

        1. Фильтрует товары по имени.
        2. Обновляет поле discount.
        3. Выводит количество изменённых записей.
        """
        self.stdout.write("Start demo bulk actions products update")  # Лог начала команды

        # Массовое обновление поля discount для всех товаров, содержащих "Smartphone" в имени
        result = Product.objects.filter(
            name__contains="Smartphone", # __contains — это оператор Django для SQL LIKE '%Smartphone%'
        ).update(discount=10) # Обновляем поле discount на 10

        print(result)  # Вывод количества обновлённых записей

        self.stdout.write("Done")  # Лог завершения команды