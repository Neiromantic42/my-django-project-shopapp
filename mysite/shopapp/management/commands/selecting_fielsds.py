from django.contrib.auth.models import User          # Модель пользователя Django
from django.core.management import BaseCommand       # Базовый класс management-команд
from shopapp.models import Product                   # Модель продукта


class Command(BaseCommand):
    """
    Демонстрационная management-команда.

    Показывает:
    - выборку только нужных полей через values()
    - получение одного поля через values_list()
    - отличие QuerySet от обычного списка
    """
    help = "Get a promotional code"                   # Описание команды

    def handle(self, *args, **options):
        """
        Точка входа команды.

        Выполняет выборку данных из БД и выводит их в консоль.
        """
        self.stdout.write("Start demo select fields") # Лог начала выполнения

        products_values = Product.objects.values("pk", "name")  # Запрос только pk и name
        for product in products_values:               # Итерация выполняет SQL-запрос
            print(product)                             # product — словарь полей

        users_info = User.objects.values_list("username", flat=True)  # QuerySet usernames
        print(list(users_info))                        # Материализация QuerySet в список

        for u_i in users_info:                         # Повторная итерация из кэша
            print(u_i)                                 # u_i — строка username

        self.stdout.write("Done")                      # Лог завершения
