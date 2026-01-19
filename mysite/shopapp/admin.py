from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products, save_file_orders
from .models import Product, Order, ProductImages
from .admin_mixins import ExportAsCsvMixin
from .forms import CSVImportForm, FileImportForm



class OrderInline(admin.TabularInline):
    """
    Inline-класс для редактирования заказов, связанных с продуктом.
    Используется в ProductAdmin для того, чтобы на странице продукта
    можно было видеть и изменять все заказы, в которых этот продукт участвует.
    """
    model = Product.orders.through
    # указываем промежуточную таблицу ManyToMany (через 'through'),
    # чтобы редактировать связи Product ↔ Order


class ProductInline(admin.StackedInline):
    """
    Inline-класс для отображения и редактирования дополнительных изображений продукта
    прямо на странице редактирования продукта в админке Django.

    Позволяет:
    - просматривать все изображения, связанные с продуктом,
    - добавлять новые изображения,
    - редактировать описание изображения,
    - удалять изображения без перехода на отдельную страницу.
    """

    # Указываем модель, которая будет отображаться внутри страницы продукта.
    # Здесь это ProductImages — дополнительные изображения для продукта.
    model = ProductImages

    # StackedInline означает вертикальное расположение полей (по умолчанию)
    # Каждое изображение будет в отдельной "панели" с полями image и description.
    # Если бы использовали TabularInline — строки были бы в виде таблицы.


@admin.action(description="Архивация продуктов")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """Функция, которая выполнит архивацию продукта."""
    queryset.update(archived=True) # все записи которые были выделены в админке попадут в queryset, и затем массово обновятся(заархивируются)

@admin.action(description="Разархивация продуктов")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """Функция, которая выполнит разархивацию продукта """
    queryset.update(archived=False) # все записи которые были выделены в админке попадут в queryset, и затем массово обновятся(заархивируются)


@admin.register(Product)  # Регистрируем модель Product в админке (короткая запись)
class ProductAdmin(admin.ModelAdmin, ExportAsCsvMixin):
    """
    Настройка отображения модели Product в админке.
    Включает:
    - отображение колонок продукта в списке (list_display)
    - кликабельные поля (list_display_links)
    - сортировку по умолчанию (ordering)
    - поиск по текстовым и числовым полям (search_fields)
    - фильтры справа для быстрого отбора объектов (list_filter)
    - метод для отображения укороченного описания продукта (description_short)
    """
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archived, mark_unarchived, "export_csv",
    ]  # Добавляем новое действие в админку (массовая архивация\разархивация)

    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    # какие поля показывать в таблице (pk, имя, описание короткое, цена, скидка)

    # list_display = "pk", "name", "description", "price", "discount"
    # альтернатива — если хотим показывать полное описание вместо короткого

    list_display_links = "pk", "name"
    # какие поля в таблице будут ссылками для перехода к редактированию

    ordering = "pk",
    # сортировка по умолчанию (здесь по pk = id)

    search_fields = "name", "price", "description"
    # поиск по этим полям (вверху появится строка поиска)

    # фильтры справа, чтобы быстро отбирать объекты по:
    list_filter = ("discount", "created_at", "archived")

    inlines = [
        OrderInline,  # Показывать связанные заказы прямо на странице продукта
        ProductInline,  # Показывать дополнительные изображения продукта внутри страницы продукта
    ]

    fieldsets = [
        (None, {
            "fields": ("name", "description"),
            "classes": ("wide",),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("collapse", "wide"),
        }),
        ("Images", {
            "fields": ("preview",),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Если установлено, товар считается устаревшим или недоступным для покупки"
        })
    ]

    def description_short(self, obj: Product) -> str:
        # метод для отображения укороченного описания
        if len(obj.description) <= 48:
            # если описание короче 48 символов — показываем как есть
            return obj.description
        return obj.description[:48] + "..."
        # иначе обрезаем и добавляем "..."

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        # Вьюха для загрузки CSV файла
        if request.method == "GET":
            form = CSVImportForm()
            # Создаём экземпляр формы
            context = {"form": form}
            # Контекст для шаблона
            return render(request, 'admin/csv_fom.html', context=context)
            # Рендерим форму в кастомном шаблоне админки

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_fom.html', context=context, status=400)

        save_csv_products( # вызываем функцию save_csv_products, которая прочитает CSV и создаст объекты Product в базе
            file=form.files["csv_file"].file,  # берем файл CSV из загруженных через форму (поле "csv_file")
            encoding=request.encoding,  # используем кодировку запроса, чтобы правильно читать текст
        )
        return redirect(
            "..")  # перенаправляем пользователя обратно на список продуктов в админке после успешного импорта

    def get_urls(self):
        # Переопределяем URLs админки
        urls = super().get_urls()
        # Берём стандартные URL админки
        new_urls = [
            path("import-products-csv/", self.import_csv, name="import_products_csv"),
            # Добавляем URL для импорта CSV
        ]
        return new_urls + urls
        # Объединяем новые и стандартные URL


# admin.site.register(Product, ProductAdmin)
# Альтернативная регистрация (не используется, так как выше есть @admin.register)

# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    """
    Inline-редактор для связи Order ↔ Product через промежуточную таблицу ManyToMany.
    Позволяет добавлять, удалять и изменять продукты прямо на странице заказа.
    """
    # model = Product # Используется, если у тебя обычная ForeignKey на родительскую модель
    model = Order.products.through # Используется, если связь ManyToMany.
    # through — это промежуточная таблица, которую Django создаёт автоматически для ManyToMany





@admin.register(Order)  # Регистрируем модель Order в админке
class OrderAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Order в админке.
    Включает:
    - отображение колонок заказа в списке (list_display),
    - кликабельные поля (list_display_links),
    - inline-редактирование связанных продуктов через ProductInline,
    - оптимизацию запросов с select_related для пользователя,
    - кастомное отображение имени пользователя через метод user_verbose.
    """
    change_list_template = "shopapp/order_change_list.html"

    list_display = "delivery_address", "promocode", "created_at", "user_verbose"
    # показываем адрес доставки, промокод и дату создания

    list_display_links = "delivery_address", "promocode"
    # эти поля будут ссылками для перехода к редактированию

    inlines = [ProductInline ] # подключаем inline-редактирование продуктов

    def get_queryset(self, request):
        """Метод для подгрузки связанного обькта с заказом отношение один к одному или один ко многим """
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        """
        Возвращает имя пользователя для отображения в админке.
        Если first_name пустое, показывает username.
        Используется в list_display для кастомной колонки.
        """
        return obj.user.first_name or obj.user.username

    def import_json(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает загрузку файла с заказами через админку.

        Показывает форму для загрузки и сохраняет данные из файла в базу.
        """
        if request.method == "GET":
            form = FileImportForm()
            context = {
                "form": form
            }
            return render(request, 'admin/csv_fom.html', context=context)

        form = FileImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_fom.html', context, status=400)

        save_file_orders(
            file=form.files["file"].file, # берем файл CSV из загруженных через форму (поле "file")
            encoding=request.encoding, # используем кодировку запроса, чтобы правильно читать текст
        )
        return redirect(
            "..")  # перенаправляем пользователя обратно на список заказов


    def get_urls(self):
        # Переопределяем URLs админки
        urls = super().get_urls() # Берём стандартные URL админки
        new_urls = [
            path("import-orders-file/", self.import_json, name="import_orders_file")
        ]
        return new_urls + urls