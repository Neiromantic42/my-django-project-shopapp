from django.contrib.auth.models import User, Group, Permission  # Импортируем встроенные модели пользователей, групп и прав доступа
from django.core.management import BaseCommand  # Импортируем базовый класс для создания собственных management-команд


class Command(BaseCommand):
    """
    Класс-команда для назначения пользователю прав через группу
    """
    def handle(self, *args, **options):
        # Получаем пользователя с id=4 из базы данных
        user = User.objects.get(pk=4)

        # Ищем группу с именем "profile_manager", если её нет — создаём
        group, created = Group.objects.get_or_create(
            name="profile_manager",
        )

        # Получаем объект права (permission) с кодовым именем "view_profile"
        # Это стандартное право Django для модели Profile.
        # Оно разрешает пользователю **просматривать профили** в админке или в приложении.
        permission_profile = Permission.objects.get(
            codename="view_profile",
        )

        # Получаем объект права с кодовым именем "view_logentry"
        # Это право разрешает пользователю **просматривать журнал действий в админке** (кто что добавлял, изменял, удалял).
        permission_logentry = Permission.objects.get(
            codename="view_logentry"
        )

        # Добавляем право view_profile в группу profile_manager
        # Теперь все пользователи, которые будут состоять в этой группе, смогут просматривать профили
        group.permissions.add(permission_profile)
        # присоединяем пользователя к группе
        user.groups.add(group)
        # связать пользователя напрямую с разрешением
        user.user_permissions.add(permission_logentry)
        # сохраняем изменения в группе
        group.save()
        # сохраняем изменения в пользователе
        user.save()