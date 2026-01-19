from django.contrib.auth.models import User  # импорт модели пользователя Django
from django.db import models  # импорт модулей для создания моделей
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

def product_preview_directory_path(instance: "Product", filename: str) -> str:
    """
    instance → объект модели Product
    filename → исходное имя загруженного файла
    Сохраняем файлы по папкам вида: products/<id_товара>/<имя_файла>
    """
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )

class Product(models.Model):
    """
    Модель Product представляет товар,
    А точнее 1 единицу товара(1-строка из табл.бд shopapp_product)

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        """
        Класс мето информации о модели включает в себя:
        -пред сортировку по имени товара и цене
        -человекочитаеморе имя в единственном числе, переведенное на Русский язык
        -человекочитаеморе имя во множественном числе, переведенное на Русский язык
        """
        ordering = ['name', 'price']  # сортировка по умолчанию: сначала по имени (A→Я), потом по цене (дороже первыми)
        # db_table = 'product'  # явное имя таблицы в БД (по умолчанию было бы appname_product)
        verbose_name = _('Product')
        verbose_name_plural = _('products')  # добавляем перевод для админки в человеко-читаемой форме
    name = models.CharField(max_length=100, db_index=True)  # название продукта, индексированное поле
    description = models.TextField(  # описание продукта
        null=False, # в БД не может быть значение NULL
        blank=True, # может быть пустым в форме (в бд сохраниться пустая строка)
        db_index=True # индексированное поле (обеспечивается эффективность)
    )
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)  # цена продукта, точная денежная величина
    discount = models.SmallIntegerField(default=0)  # скидка, маленькое целое число
    # Автор продукта: связь с пользователем, который создал продукт.
    # Если пользователь будет удалён, поле станет NULL (продукт останется в базе).
    # related_name='products' позволяет получить все продукты пользователя через user.products.all()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)  # время создания продукта автоматически
    archived = models.BooleanField(default=False)  # флаг архивирования продукта(True=архивирован, False=доступен)
    preview = models.ImageField( # Поле для хранения картинки-превью товара
        null=True, # null=True → в базе можно хранить NULL, т.е. картинка необязательна
        blank=True, # blank=True → форма будет принимать пустое значение (не обязательна для заполнения)
        upload_to=product_preview_directory_path # upload_to=product_preview_directory_path → функция,
        # которая возвращает путь для сохранения файла
    )

    def __str__(self) -> str:
        """
        Строковое представление экземпляра класса
        """
        return f"Product(pk={self.pk}, name={self.name!r}, author={self.created_by!r})"

    def get_absolute_url(self):
        """
        метод для sitemap

        возвращает ссылку на конкретный товар
        """
        return reverse("shopapp:products_details", kwargs={"pk": self.pk})


def product_images_directory_path(instance: "ProductImages", filename: str) -> str:
    """
    Функция для формирования пути сохранения изображений продукта
    - instance: объект модели ProductImages, для которого загружается файл.
    - filename: исходное имя загружаемого файла.
    """
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,   # <-- pk продукта, к которому относится изображение
        filename=filename,        # <-- оригинальное имя файла (не меняем)
    )

class ProductImages(models.Model):
    """
    Модель, которая хранит дополнительные изображения продукта.
    """
    # Связь с продуктом: одно изображение принадлежит одному продукту.
    # related_name="images" → к продукту можно обратиться product.images.all()
    # on_delete=models.CASCADE → если продукт удалят, его изображения тоже удалятся
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    # Сам файл изображения; upload_to задаёт функцию, которая формирует путь для сохранения
    image = models.ImageField(
        upload_to=product_images_directory_path,
        )
    # Короткое текстовое описание изображения (необязательно для формы)
    description = models.CharField(max_length=200, null=False, blank=True)



class Order(models.Model):
    """Модель таблицы заказов"""
    class Meta:
        """Метоинформация для админки и дефолт сортировка по дате создания"""
        ordering = ['created_at']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')# добавляем перевод для админки в человеко-читаемой форме

    delivery_address = models.TextField(null=True, blank=True)  # адрес доставки, может быть пустым
    promocode = models.CharField(max_length=20, null=False, blank=True)  # промокод, строка до 20 символов, нельзя NULL
    created_at = models.DateTimeField(auto_now_add=True)  # дата и время создания заказа
    # Связи с юзером один ко многим и связь с продуктом многие ко многим
    user = models.ForeignKey(User, on_delete=models.PROTECT)  # связь с пользователем(многие к одному), защита от удаления
    products = models.ManyToManyField(Product, related_name="orders")  # связь многие-ко-многим с продуктами, обратная ссылка orders
    receipt = models.FileField( # Поле для хранения загруженного файла (например, квитанции заказа)
        null=True, # null=True → разрешает хранить пустое значение в базе, т.е. файл необязательный
        upload_to='orders/receipt' # upload_to='orders/receipt' → файлы будут сохраняться в папку MEDIA_ROOT/orders/receipt/
    )

    def __str__(self) -> str:
        """
        Строковое представление экземпляра класса.
        """
        return f"Order(pk={self.pk}, user_name={self.user.last_name + self.user.first_name})"
