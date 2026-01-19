from django.core.management import BaseCommand
# Импортируем базовый класс BaseCommand для создания кастомной команды Django

from shopapp.models import Product
# Импортируем модель Product из приложения shopapp, чтобы работать с объектами этой модели

class Command(BaseCommand):
    # Создаём класс команды, наследуемый от BaseCommand
    # Django ищет этот класс при запуске команды через manage.py

    help = "Creates products"
    # Документация команды, отображается при python manage.py help <command>

    def handle(self, *args, **options):
        # Основной метод, который выполняется при запуске команды
        # *args — позиционные аргументы команды (если есть)
        # **options — именованные аргументы/опции команды

        self.stdout.write("Create products")
        # Выводим в консоль сообщение о начале работы команды

        products_name = [
            "Laptop",
            "Desktop",
            "Smartphone"
        ]
        # Список названий продуктов, которые хотим добавить в базу

        for name in products_name:
            # Цикл по списку названий продуктов
            # name — текущее имя продукта на каждой итерации

            product, created = Product.objects.get_or_create(name=name)
            # get_or_create() пытается найти объект с таким именем
            # Если объект существует — возвращает его, created=False
            # Если объекта нет — создаёт новый и created=True
            # product — объект Product
            # created — логическое значение, создан ли объект

            self.stdout.write(f"Created product {product.name}")
            # Выводим в консоль сообщение о каждом созданном или найденном продукте
            # f-string подставляет имя продукта

        self.stdout.write(self.style.SUCCESS("Products created"))
        # Выводим итоговое сообщение об успехе
        # self.style.SUCCESS — зелёный текст в консоли для успеха