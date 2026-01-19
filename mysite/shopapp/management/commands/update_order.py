from django.core.management import BaseCommand  # Импорт базового класса для создания команды Django
from shopapp.models import Order, Product  # Импортируем модели Order и Product из приложения shopapp

class Command(BaseCommand):
    """
    Команда для добавления в заказ продуктов
    """
    help = "Update order"  # Описание команды, показывается при помощи 'python manage.py help'

    def handle(self, *args, **options):  # Основной метод, который выполняется при запуске команды
        self.stdout.write("Update order")  # Выводим сообщение в консоль, что команда запущена

        order = Order.objects.first()  # Получаем первый заказ из базы данных
        if not order:  # Если заказов нет
            self.stdout.write("No order found")  # Сообщаем, что заказ не найден
            return  # Прерываем выполнение команды

        products = Product.objects.all()  # Получаем все продукты из базы данных

        for product in products:  # Перебираем каждый продукт
            order.products.add(product)  # Добавляем продукт в ManyToMany связь с заказом

        order.save()  # Сохраняем изменения (для ManyToMany save не обязателен, но можно оставить)

        # Выводим сообщение об успешном выполнении с перечнем продуктов и самим заказом
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added products {order.products.all()} to order {order}"
            )
        )