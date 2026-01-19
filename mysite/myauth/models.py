from django.contrib.auth.models import User  # Импорт встроенной модели пользователя Django
from django.db import models  # Импорт базового модуля для описания моделей


def profile_avatar_upload_to_path(instance: "Profile", filename: str) -> str:
    # instance → объект модели Profile
    # filename → исходное имя загруженного файла

    # Сохраняем файлы по папкам вида: orders/<id_профиля>/<имя_файла>
    return "profiles/profile_{pk}/avatar/{filename}".format(
        pk=instance.user.pk,
        filename=filename
    )

class Profile(models.Model):
    """
    Модель профиля, расширяющая данные стандартного пользователя
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")  # Связь "один к одному"
    # с пользователем; при удалении пользователя — профиль тоже удаляется
    bio = models.TextField(max_length=500, blank=True)  # Поле для биографии (необязательное, до 500 символов)
    agreement_accepted = models.BooleanField(default=False)  # Флаг согласия с условиями (по умолчанию — не принято)
    avatar = models.ImageField(
        null=True, # null=True → в базе можно хранить NULL, т.е. картинка необязательна
        blank=True, # blank=True → форма будет принимать пустое значение (не обязательна для заполнения)
        upload_to=profile_avatar_upload_to_path # upload_to=profile_avatar_upload_to_path → функция,
        # которая возвращает путь для сохранения файла
    )