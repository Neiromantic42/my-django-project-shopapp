from django.contrib.auth.models import User, Group, Permission
# Импортируем модели User, Group и Permission из Django для работы с пользователями, группами и правами
from django.core.management import BaseCommand
# Импортируем BaseCommand, чтобы создать кастомную команду manage.py

class Command(BaseCommand):
    """
    Класс-команда для назначения пользователю прав для создания продукта
    """

    def handle(self, *args, **options):
        # Основной метод команды, который вызывается при запуске: python manage.py <имя_команды>
        user_pavel = User.objects.get(username="Паша")
        # Получаем объект пользователя с username "Паша" из базы данных
        user_ivan = User.objects.get(last_name="Иванов")
        # Получаем объект пользователя с фамилией "Иванов" из базы данных
        permission_add_product = Permission.objects.get(
            codename="add_product"
        )
        # Получаем объект разрешения с кодовым именем "add_product", которое позволяет создавать продукты
        user_pavel.user_permissions.add(permission_add_product)
        # Добавляем пользователю Павлу право создавать продукты
        user_ivan.user_permissions.add(permission_add_product)
        # Добавляем пользователю Иванову право создавать продукты
        user_ivan.save()
        # Сохраняем изменения пользователя Иванова в базе данных
        user_pavel.save()
        # Сохраняем изменения пользователя Павла в базе данных