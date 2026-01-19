"""
В этом модуле лежат различные наборы представлений.

Для интернет-магазина: сущности для CRUD операций над товарами и заказами.
"""
import logging # импортируем модуль логирования

from timeit import default_timer
from csv import DictReader, DictWriter
from django.contrib.auth.models import Group, User
from django.views.decorators.cache import cache_page
from django.core.cache import cache
# Декоратор для кеширования результата view (HTTP-ответа) на заданное время
from django.utils.decorators import method_decorator
# Утилита для применения декораторов (например cache_page) к методам class-based views
from django.contrib.syndication.views import Feed

from django.urls import reverse_lazy
from django.views import View  # Импорт класса вью
# Импорт классов представлений Django для работы с:
# шаблонами, списками, деталями, созданием, обновлением и удалением объектов
from django.views.generic import (
    ListView,       # список объектов
    DetailView,     # детали одного объекта
    CreateView,     # создание нового объекта
    UpdateView,     # редактирование существующего объекта
    DeleteView      # удаление объекта
)
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet  # базовый класс для создания API viewset с CRUD операциями (list, create, retrieve, update, destroy)
from rest_framework.filters import SearchFilter, OrderingFilter   # встроенный фильтр DRF для поиска по полям модели через query parameters
from rest_framework.decorators import action # позволяет подкл. любую view функцию к классу обработчику ViewSet
from django_filters.rest_framework import DjangoFilterBackend

# Декоратор для добавления метаданных к API-эндпоинту для генерации схемы
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Product, Order, ProductImages
from django.http import HttpResponse, HttpRequest, JsonResponse, \
    HttpResponseRedirect  # Импортируем класс HttpResponse, чтобы возвращать простой HTTP-ответ (текст, HTML и т.д.)

from django.shortcuts import render, redirect, reverse, get_object_or_404
# Импортируем функцию render для возвращения HTML-шаблонов с данными (не используется в этом примере)

from .forms import ProductForm, OrderForm, GroupForm  # Импорт HTML-форм
from .serializers import ProductSerializer, OrderSerializer # Импорт сериализатора для API
from .common import save_csv_products

from django.contrib.auth.mixins import ( # Миксины для ограничения доступа к класс-представлениям (views).
    LoginRequiredMixin,  # Требует, чтобы пользователь был авторизован (вошёл в систему).
    PermissionRequiredMixin,  # Требует наличия у пользователя определённого разрешения (permission).
    UserPassesTestMixin  # Позволяет задать собственную функцию проверки (test_func),
)

log = logging.getLogger(__name__) # Создаем логгер

class LatestProductsFeed(Feed):
    """
    Класс-представление (RSS) для ленты новостей.

    RSS лента позволяет подписчикам получать последние продукты автоматически.
    """
    title = "Products in the store (latest)" # Заголовок для rss-ленты
    description = "Updates on changes and product additions to the store" # Описание ленты
    link = reverse_lazy("shopapp:products_list") # Ссылка на страницу со списком товаров

    def items(self):
        """
        Метод возвращает список объектов, которые будут включены в RSS-ленту.

        Каждый объект будет обрабатываться методами item_title, item_description и item_link.
        """
        return (
            Product.objects
            .filter(archived=False)
            .order_by("-created_at")[:10]
        )


    def item_title(self, item: Product):
        """
        Метод формирует заголовок для каждого элемента RSS-ленты.

        Django вызывает этот метод для каждого объекта из items().
        """
        return item.name

    def item_description(self, item: Product):
        """
        Метод формирует описание товара
        """
        return item.description[:100]



@method_decorator(cache_page(60 * 1), name="list")
@extend_schema(description=(
        "Набор представлений для действий над Product. "
        "Полный CRUD для сущностей товара."
    )
)
class ProductViewSet(ModelViewSet):
    """
    ViewSet для REST, CRUD-операций над товарами.

        GET /api/products/ → список всех товаро
        GET /api/products/<id>/ → детали товара
        POST /api/products/ → создание нового товара
        PUT /api/products/<id>/ → полное обновление
        PATCH /api/products/<id>/ → частичное обновление
        DELETE /api/products/<id>/ → удаление товара
    """
    queryset = Product.objects.all()  # Получаем все товары из БД
    serializer_class = ProductSerializer  # Используем наш сериализатор для API

    filter_backends = [ # указываем какие фильтры используем, здесь по умолчанию DjangoFilterBackend + SearchFilter
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter, # сортировка
    ]

    search_fields = [ # указываем по каким полям надо выполнять поиск SearchFilter
        "name", "description"
    ]

    filterset_fields = [ # Указываем поля, по которым будет осуществляться фильтрация
        "name",
        "description",
        "price",
        "discount",
        "archived"
    ]

    ordering_fields = [ # Указываем поля, по которым будет осуществлена сортировка
        "name",
        "description",
        "price",
    ]

    @extend_schema(
        summary="Получить один конкретный product по id, в рамках полного CRUD-View",
        # Краткое описание метода retrieve для Swagger UI — отображается как заголовок операции в документации.
        description="Получает **product**, возвращает ошибку 404, если не найден.",
        # Подробное описание метода retrieve — отображается под summary, можно использовать Markdown для выделения.
        responses={
            # Словарь возможных HTTP-ответов метода: статус-код → сериализатор или описание ответа
            200: ProductSerializer,
            # Статус 200 OK — успешный ответ возвращает сериализованный объект Product
            404: OpenApiResponse(description="No Product matches the given query."),
            # Статус 404 — возвращается, если продукт не найден; описываем текст ошибки
        }
    )
    def retrieve(self, *args, **kwargs):
        # Переопределяем метод retrieve из ModelViewSet (GET /api/products/<id>/)
        return super().retrieve(*args, **kwargs)
        # Вызываем стандартный метод родителя, чтобы вернуть объект Product по id

    @extend_schema(
        summary="Получить все товары, в рамках полного CRUD-View",
        # Короткое описание метода list для Swagger UI
        description="Получает список словарей всех товаров в магазине"
        # Подробное описание метода list
    )
    def list(self, *args, **kwargs):
        # Переопределяем метод list из ModelViewSet (GET /api/products/)
        log.info("Hello cache")
        return super().list(*args, **kwargs)
        # Вызываем стандартный метод родителя, чтобы вернуть список всех Product

    @action(methods=["get"], detail=False)
    # @action — DRF-декоратор для добавления кастомного endpoint’а к ViewSet
    # methods=["get"] — указываем, что этот endpoint доступен по HTTP GET
    # detail=False — значит endpoint НЕ для одного объекта,
    #                а для всей коллекции (URL будет /api/products/download_csv/)

    def download_csv(self, request: Request):
        # Метод ViewSet, который будет обрабатывать GET-запрос

        response = HttpResponse(content_type="text/csv")
        # Создаём HTTP-ответ вручную
        # content_type="text/csv" — говорим браузеру, что это CSV-файл

        filename = "product-export.csv"
        # Имя файла, которое увидит пользователь при скачивании

        response["Content-Disposition"] = f"attachment; filename={filename}"
        # HTTP-заголовок Content-Disposition
        # attachment — говорит браузеру: "это файл для скачивания, а не для отображения"
        # filename=... — имя файла при сохранении

        # self.get_queryset() возвращает все объекты (базовый queryset) = Product.objects.all()
        # self.filter_queryset(...) применяет фильтры, поиск и сортировку из запроса
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",  # выбираем только поле name
            "description",  # выбираем только поле description
            "price",  # выбираем только поле price
            "discount",  # выбираем только поле discount
        ]
        # queryset.only(...) → оптимизация: извлекаем только указанные поля в fields из базы
        # остальные поля будут загружены только при доступе к ним
        queryset = queryset.only(*fields)
        # CSV writer: пишет словари в response с колонками, указанными в fields
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader() # записывает первую строку с заголовками колонок

        for product in queryset: # перебираем каждый объект Product в queryset
            writer.writerow({ # writer.writerow(...) записывает этот словарь как строку в CSV
                field: getattr(product, field) for field in fields # для каждой строки формируем словарь: ключ = имя поля, значение = атрибут объекта
            })
        return response

    @action(
        methods=["post"],  # этот endpoint доступен только по POST
        detail=False,  # работает со всей коллекцией, а не с одним объектом
        parser_classes=[MultiPartParser]  # ожидаем multipart/form-data (для файлов)
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            file=request.FILES["file"].file,  # берём загруженный CSV файл из запроса
            encoding=request.encoding,  # используем кодировку запроса
        )
        serializer = self.get_serializer(products, many=True)  # сериализуем созданные объекты Product
        return Response(serializer.data)  # возвращаем данные в виде JSON


# @method_decorator(cache_page(60), name="get") # Декоратор для кеширования представления (метода get)
class ShopIndexView(View):
    """
    класс-представление, наследуемый от базового класса View.

    Реализует базовую страницу приложения - shopapp
    особо не на что не влияет, выводит грубо заданные данные
    """

    def get(self, request: HttpRequest) -> HttpResponse:  # метод get обрабатывает GET-запросы
        products = [  # список товаров с названиями и ценами
            ('laptop', 1999),
            ('Desktop', 2000),
            ('Smartphone', 6666),
        ]
        context = {             # создаём контекст — данные, которые передадим в шаблон
            "time_running": default_timer(),  # текущее время работы (пример использования таймера)
            "products": products,             # список товаров для отображения на странице
            "items": 1
        }
        log.setLevel("DEBUG")
        log.debug("Product for shop index: %s", context)
        log.info("Rendering shop-index.html")
        return render(request, 'shopapp/shop-index.html', context=context)  # возвращаем HTML-страницу с переданными данны


def store_services(request: HttpRequest):
    """
    Вью-функция, для демонстрации услуг магазина
    """
    services = [
        {'name': 'laptop', 'description': 'software installation', 'price': 1500.51},
        {'name': 'desktop', 'description': 'collect', 'price': 1000.15},
        {'name': 'smartphone', 'description': 'stick protective glass', 'price': 800.67},
    ]
    context = {
        "services": services
    }
    return render(request, 'shopapp/store-services.html', context=context)



class GroupsListView(View):  # создаём класс-представление для работы с группами
    """
    Клас обработчик который служит для показа всех групп по get и
    добавления новой группы по post - запросу
    """
    def get(self, request: HttpRequest) -> HttpResponse:  # обработка GET-запроса
        """
        Функция для демонстрации групп пользователей с разрешениями
        """  # описание метода
        context = {
            "form" : GroupForm(),  # создаём пустую форму для добавления новой группы
            "groups": Group.objects.prefetch_related('permissions').all(),  # получаем все группы с их разрешениями
        }
        return render(request, 'shopapp/groups-list.html', context=context)  # возвращаем HTML-страницу с данными

    def post(self, request: HttpRequest):  # обработка POST-запроса
        """
        Функция для создания группы пользователей
        """  # описание метода
        form = GroupForm(request.POST)  # передаём данные из POST-запроса в форму
        if form.is_valid():  # проверяем, корректны ли данные формы
            form.save()  # сохраняем новую группу в базу данных

        return redirect(request.path)  # после сохранения перенаправляем обратно на ту же страницу




class UserOrdersListView(LoginRequiredMixin, ListView):
    """
    Отображает список заказов выбранного пользователя.

    ID пользователя передаётся в URL.
    Доступ разрешён только авторизованным пользователям.
    Если пользователь не найден — возвращается 404.
    """
    template_name = "shopapp/current_users_order_page.html"  # Шаблон страницы
    context_object_name = "orders"  # Имя переменной со списком заказов в шаблоне
    owner: User  # Атрибут для хранения пользователя (нужен для контекста и типизации)

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs["user_id"] # Получаем ID пользователя из URL
        self.owner = get_object_or_404(User, pk=user_id) # Загружаем пользователя или возвращаем 404
        # Формируем queryset заказов пользователя
        orders = (
            Order.objects
            .select_related("user")        # Оптимизация FK (Order → User)
            .prefetch_related("products")  # Оптимизация M2M (Order → Products)
            .filter(user_id=user_id)       # Фильтрация заказов по пользователю
        )
        return orders # Возвращаем queryset для ListView

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs) # Получаем стандартный контекст ListView
        context["owner"] = self.owner # Передаём пользователя в шаблон (НЕ текущего user, а владельца заказов)
        return context


class OrdersUserDataExport(View):
    """
    Возвращает заказы выбранного пользователя в JSON формате.
    Кеширует результат на 60 секунд, чтобы повторные запросы не обращались к базе.
    """

    def get(self, request: HttpRequest, user_id: int) -> JsonResponse:
        user = get_object_or_404(User, id=user_id)  # Получаем пользователя или 404

        cache_key = f"user_orders_{user_id}"  # Генерируем уникальный ключ для кеша
        cache_data = cache.get(cache_key)  # Пытаемся взять данные из кеша

        if cache_data is None:   # Если кеш пуст
            queryset = (  # Загружаем заказы пользователя
                Order.objects
                .select_related("user")  # Оптимизация для FK user
                .prefetch_related("products")  # Оптимизация для M2M products
                .filter(user_id=user.pk)   # Только заказы выбранного пользователя
                .order_by("id")   # Сортировка по PK
            )
            log.info(queryset.query) # Логируем SQL-запрос для отладки
            orders_data = [ # Преобразуем queryset в список словарей
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "promocode": order.promocode,
                    "created_at": order.created_at,
                    "user_id": order.user_id,
                }
                for order in queryset
            ]
            cache.set(cache_key, orders_data, 60)  # Сохраняем результат в кеш на 60 секунд
            return JsonResponse({"orders": orders_data})  # Возвращаем JSON
        log.info("Загрузка из кеша")
        return JsonResponse({"orders": cache_data})  # Если данные в кеше — возвращаем их



class ProductsListView(ListView):
    """
    Класс-представление для отображения списка товаров.
    Наследуется от ListView — это специальный класс CBV (Class-Based View),
    предназначенный для вывода списка объектов из базы данных.
    """
    template_name = 'shopapp/products-list.html'  # Указываем путь к HTML-шаблону, который будет рендериться при обращении к этому представлению.
    # model = Product  # Задаем модель, с которой будет работать представление. Django автоматически сделает запрос Product.objects.all().
    context_object_name = "products"  # Имя переменной, под которым список объектов будет доступен в шаблоне.
    queryset = Product.objects.filter(archived = False) # Получаем только те объекты (продуктов) что не архивированные


class ProductDetailsView(DetailView):
    """
    Класс-представление для отображения страницы с подробной информацией о конкретном товаре.
    Наследуется от DetailView — это специальный класс CBV, который показывает данные одного объекта модели.
    """
    template_name = 'shopapp/product-details.html'  # Путь к HTML-шаблону, который будет использоваться для отображения страницы товара.
    # model = Product  # Указываем модель, из которой будет извлекаться конкретный объект (Product.objects.get(pk=...)).
    queryset = Product.objects.prefetch_related("images")  # Подгружаем все связанные изображения заранее для оптимизации запросов
    context_object_name = "product"  # Имя переменной, под которым объект будет доступен в шаблоне (по умолчанию — "object").


class ProductCreateView(
    PermissionRequiredMixin,
    # UserPassesTestMixin, # временно отключили кастомную проверку прав в группе
    CreateView
):
    """
    Класс-представление для создания нового продукта.

    PermissionRequiredMixin:
    - Позволяет ограничить доступ к представлению на основе разрешений (permissions).
    - Проверяет, есть ли у пользователя конкретное право (permission_required) для данной модели.
    - Если

    UserPassesTestMixin:
    - Позволяет определить свою проверку доступа через метод test_func.
    - Если test_func возвращает True — пользователь может создать продукт.
    - Если False — доступ запрещён (по умолчанию PermissionDenied).

    CreateView:
    - Стандартное класс-представление Django для создания объектов модели.
    - Обрабатывает GET (показ формы) и POST (сохранение формы) автоматически.
    """
    # Право, необходимое для доступа к странице (требует разрешения "создавать продукты")
    permission_required = ['shopapp.add_product']

    model = Product # Модель с которой будем работать
    # fields = "name", "price", "description", "discount" # Поля которые будем создавать
    form_class = ProductForm # Если нужна форма с какой-то специальной проверкой ->
    # Её можно указать так, но выбрать что-то одно: или fields, или form_class.
    success_url = reverse_lazy("shopapp:products_list") # Указываем куда перенаправлять пользователя

    def form_valid(self, form):
        """переопределяем метод родителя, для привязки текущего пользователя к продукту"""
        # Добавляем к объекту Product в поле created_by текущего/залогиненного юзера
        # form.instance — это объект модели (Product), который создаётся формой, но ещё не сохранён в базе.
        # Через instance можно установить дополнительные поля до сохранения, например автор или дату.
        form.instance.created_by = self.request.user
        # Вызываем родительский form_valid:
        # 1) сохраняет объект пользователя в базу (self.object = form.save())
        # 2) возвращает редирект на success_url
        response = super().form_valid(form)
        # цикл для прохода по списку файлов взятый из объекта формы
        for image in form.files.getlist("images"):
            ProductImages.objects.create( # создаем ProductImages
                product=self.object, # Для связи передаем обьект продукта
                image=image # Передаем сам фаил
            )
        return response  # Возвращаем редирект, который вернул родительский метод form_valid


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    """
    Класс-представление для обновления существующего продукта

    UserPassesTestMixin:
    - Позволяет определить свою проверку доступа через метод test_func.
    - Если test_func возвращает True — пользователь может создать продукт.
    - Если False — доступ запрещён (по умолчанию PermissionDenied).
    """
    model = Product # Модель с которой будем работать
    # fields = "name", "price", "description", "discount", "preview" # Поля, которые будем обновлять
    # template_name_suffix = "_update_form"
    form_class = ProductForm # указываем форму для создания продукта с возможностью загрузки множества файлов
    template_name = "shopapp/product_update_form.html" # указываем шаблон для обновления продукта

    def get_success_url(self):
        return reverse(  # Генерируем URL по имени маршрута
            "shopapp:products_details",  # Имя URL-шаблона для деталей продукта
            kwargs={"pk": self.object.pk}  # Передаем pk текущего объекта продукта
        )

    def test_func(self):
        prodict = self.get_object() # безопасно возвращает экземпляр модели по pk из URL.
        return (
                self.request.user.is_superuser  # Суперюзер всегда может редактировать
                or prodict.created_by == self.request.user  # Автор продукта может редактировать
                or self.request.user.has_perm('shopapp.change_product')
                # Пользователь с правом change_product может редактировать
        )

    def form_valid(self, form):
        # Вызываем стандартный метод form_valid родительского класса
        # Сохраняет объект модели (Product) и возвращает HTTP-ответ
        response = super().form_valid(form)

        # Перебираем все файлы, которые были загружены в поле "images"
        # form.files.getlist("images") возвращает список всех выбранных файлов
        for image in form.files.getlist("images"):
            ProductImages.objects.create( # Создаём новый объект ProductImages для каждого файла(картинки)
                product=self.object, # связываем изображение с только что сохранённым продуктом
                image=image # сохраняем сам файл
            )
        # Возвращаем ответ родительского метода (обычно перенаправление на success_url)
        return response


class ProductDeleteView(DeleteView):
    """
    Класс-представление для удаления записи о продукте.
    В данном случае реализуется "мягкое удаление" — вместо физического удаления
    объект помечается как архивированный (archived = True).
    """
    model = Product  # Модель, с которой будет работать DeleteView — Product
    success_url = reverse_lazy("shopapp:products_list") # Делаем реверс на страницу с продуктами после удаления
    # URL, на который перенаправляется пользователь после успешного "удаления".
    # reverse_lazy используется, чтобы ссылку можно было вычислить при запуске сервера.

    def form_valid(self, form): # Этот метод вызывается при успешной отправке формы (POST)
        success_url = self.get_success_url()  # Получаем URL для перенаправления после удаления
        self.object.archived = True  # Вместо удаления объекта помечаем его как архивированный
        self.object.save()   # Сохраняем изменения в базе данных
        return HttpResponseRedirect(success_url)  # Перенаправляем пользователя на указанный URL


class ProductsDataExportView(View):
    """
    Объявляем класс представления, наследуем от базового View Django
    Класс чисто тестовый
    """
    def get(self, request: HttpRequest) -> JsonResponse:
        # Метод для обработки GET-запроса
        # request: объект HttpRequest, который содержит данные запроса
        # -> JsonResponse: указываем, что метод вернёт JSON-ответ
        cache_key = "products_data_export" # Создаем ключ кеша
        cache_data = cache.get(cache_key) # Получаем данные из кэша по ключу "products_data_export"
        if cache_data is None:
            # Получаем все объекты Product из базы, отсортированные по первичному ключу (pk)
            # .all() здесь можно опустить, но так читается явно
            products = Product.objects.order_by("pk").all()

            # Создаём список словарей с нужными полями для каждого продукта
            # Это list comprehension — компактный способ создать список на лету
            product_data = [
                {   # Для каждого продукта создаём словарь с полями:
                    "pk": product.pk,          # первичный ключ продукта
                    "name": product.name,      # имя продукта
                    "price": str(product.price),    # цена продукта
                    "archived": product.archived # статус архивированности
                }
                for product in products  # перебираем все продукты из QuerySet
            ]
            cache.set(cache_key, product_data, 60) # Добавляем в кэш: ключ кэша, данные товаров, время жизни кэша
            # Вносим намеренную ошибку для (Sentry)
            elem = product_data[0]
            # name = elem["neme"] # Намеренная ошибка
            name = elem["name"]
            print("name:", name)

            # Возвращаем JSON-ответ, словарь превращается в JSON автоматически
            # В ключе "products" лежит список словарей, описанных выше
            return JsonResponse({"products": product_data})

        # если кэш не пуст, возвращаем данные товаров из него!
        return JsonResponse({"products": cache_data})


class OrderViewSet(ModelViewSet):
    """
    ViewSet для REST, CRUD-операций над заказами (Order) :
        GET /api/orders/ → список всех заказов
        GET /api/orders/<id>/ → детали конкретного заказа
        POST /api/orders/ → создание нового заказа
        PUT /api/orders/<id>/ → полное обновление заказа
        PATCH /api/orders/<id>/ → частичное обновление заказа
        DELETE /api/orders/<id>/ → удаление заказа
    """
    queryset = ( # Получаем все объекты Order из базы данных
        Order.objects.select_related("user")
        .prefetch_related("products")
        .all()
    )
    serializer_class = OrderSerializer  # Используем сериализатор OrderSerializer для преобразования данных в JSON и обратно

    filter_backends = [  # Определяем фильтры, которые будут применяться к запросам API
        DjangoFilterBackend,  # Фильтрация по точным значениям полей через django-filters
        SearchFilter,  # Поиск по текстовым полям, поддерживает __icontains
        OrderingFilter,  # Сортировка по указанным полям
    ]

    filterset_fields = [  # Поля, по которым можно фильтровать через GET параметры ?field=value
        "delivery_address",  # Фильтрация по адресу доставки
        "promocode",  # Фильтрация по использованному промокоду
        "created_at",  # Фильтрация по дате и времени создания заказа
        "user__username",  # Фильтрация по пользователю, создавшему заказ
        "products__name",  # Фильтрация по товарам, входящим в заказ (ManyToMany)
    ]

    search_fields = [  # Поля для текстового поиска через GET параметр ?search=...
        "delivery_address",  # Поиск по адресу доставки
        "user__username",  # Поиск по имени или идентификатору пользователя
    ]

    ordering_fields = [  # Поля, по которым можно сортировать через GET параметр ?ordering=...
        "created_at",  # Сортировка по дате создания (новые или старые заказы)
        "user_username",  # Сортировка по пользователю (по алфавиту или по id)
    ]

class OrderListView(LoginRequiredMixin, ListView):
    """
    Класс-представление для отображения списка заказов.

    Наследуется от:
      - LoginRequiredMixin — ограничивает доступ к странице только для
        авторизованных пользователей. Если пользователь не вошёл в систему,
        его автоматически перенаправит на страницу входа (LOGIN_URL).
      - ListView — стандартное представление Django, которое отображает
        список объектов из базы данных.
    """
    queryset = (
        Order.objects  # Берём менеджер модели Order, чтобы работать с записями из таблицы заказов.
        .select_related("user")  # Загружает данные пользователя одним JOIN
        .prefetch_related("products")  # Предзагружаем связанные продукты (ManyToMany) вторым запросом, чтобы потом не делать отдельный запрос для каждого заказа.
        .all()  # Завершаем формирование запроса, получая весь набор заказов.
    )
    context_object_name = 'orders' # Имя переменной, под которым список объектов будет доступен в шаблоне.


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """
    Класс-представление для отображения деталей конкретного заказа.

    Наследуется от:
      - PermissionRequiredMixin — проверяет наличие у пользователя
        определённого разрешения (permission). Если права нет, пользователь
        получает ответ 403 Forbidden.
      - DetailView — стандартное представление Django для показа
        одного объекта модели по его первичному ключу (pk).

    Пример URL:
        /shop/orders/9/ — покажет детали заказа с id=9.
    """
    # Право, необходимое для доступа к странице (требует разрешения "просматривать заказ")
    permission_required = ["shopapp.view_order"]

    queryset = (
        Order.objects  # Менеджер модели Order — используется для формирования запросов к таблице заказов.
        .select_related("user")  # Выполняет JOIN с таблицей пользователей (OneToMany), чтобы загрузить данные владельца заказа.
        .prefetch_related("products")  # Делает отдельный запрос для подгрузки связанных товаров (ManyToMany), чтобы избежать N+1 запросов.
        .all()  # Завершает запрос — получает все заказы из базы данных.
    )

    context_object_name = 'order'  # Имя переменной, под которым объект заказа будет доступен в шаблоне (например, {{ order.id }}).



class OrderCreateView(CreateView):
    """
    Клас на основе представления,
    для создания нового заказа с возможностью выбора пользователя и продуктов
    """
    model = Order # модель с которой будем работать
    form_class = OrderForm # Указываем готовую форму с валидацией входных данных

    def get_success_url(self):
        """
        переопределение метода для редиректа на
        страницу деталей заказа, после успешного создания заказа
        """
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk}
        )

class OrderUpdateView(UpdateView):
    """
    Класс представление для
    обновления текущего заказа
    """
    model = Order # модель с которой будем работать
    fields = ["delivery_address", "user" ,"promocode", "products"] # Указываем поля для обновления

    def get_success_url(self):
        """
        переопределение метода для редиректа на
        страницу деталей заказа, после успешного обновления заказа
        """
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    """
    Клас представление для
    удаления текущего заказа
    """
    model = Order # модель с которой будем работать
    success_url = reverse_lazy("shopapp:order_list")




class OrdersDataExport(UserPassesTestMixin, View):
    """
    Объявляем класс представления, наследуем от View

    Класс чисто тестовый (должен отдать список заказов)

    UserPassesTestMixin:
    - Позволяет определить свою проверку доступа через метод test_func.
    - Если test_func возвращает True — пользователь может создать продукт.
    - Если False — доступ запрещён (по умолчанию PermissionDenied).

    """
    def test_func(self):
        # проверяем, что user - это сотрудник(имеет доступ к административной панели)
        # если user.is_staff == True - доступ к View разрешен, иначе 403
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        # Метод для обработки GET-запроса
        # request: объект HttpRequest, который содержит данные запроса
        # -> JsonResponse: указываем, что метод вернёт JSON-ответ
        qs_order = (
            Order.objects # Менеджер модели Order — используется для формирования запросов к таблице заказов.
            .select_related("user") # Выполняет JOIN с таблицей пользователей (OneToMany), чтобы загрузить данные владельца заказа.
            .prefetch_related("products") # Делает отдельный запрос для подгрузки связанных товаров (ManyToMany), чтобы избежать N+1 запросов.
            .all() # Завершает запрос — получает все заказы из базы данных.
        )
        orders_data = [
            {
                "pk": order.pk, # первичный ключ заказа
                "delivery_address": order.delivery_address, # Адрес заказа
                "promocode": order.promocode, # промокод заказа
                "created_at": order.created_at, # дата создания заказа
                "user": order.user.id, # pk юзера сделавшего заказ
                "products": [product.pk for product in order.products.all()] # список pk - продуктов
            }
            for order in qs_order
        ]
        # Возвращаем JSON-ответ, словарь превращается в JSON автоматически
        # В ключе "products" лежит список словарей, описанных выше
        return JsonResponse({"orders": orders_data})
