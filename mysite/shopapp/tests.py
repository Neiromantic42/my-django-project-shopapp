from django.test import TestCase, TransactionTestCase  # Импортируем базовый класс для написания тестов в Django

from shopapp.models import Order
from .utils import add_two_number  # Импортируем тестируемую функцию из текущего пакета (модуль utils)
from django.conf import settings
from django.test import Client
from django.urls import reverse
from .models import Product, User
from string import ascii_letters
from random import choices
from faker import Faker
from django.contrib.auth.models import User, Group, Permission  # Импортируем встроенные модели пользователей, групп и прав доступа

class AddTwoNumberTestCase(TestCase):  # Определяем класс теста, который наследуется от TestCase

    def test_add_two_numbers(
            self):  # Метод, имя которого начинается с "test_", будет автоматически выполняться как тест
        result = add_two_number(2, 3)  # Вызываем тестируемую функцию с аргументами 2 и 3
        self.assertEqual(result, 5)  # Проверяем, что результат равен 5 — если нет, тест не пройдет

    def test_store_services(self):
        """
        Тест проверяет работу Вью-функция,
        для демонстрации услуг магазина (store_services)
        """
        c = Client()  # создаем обьект клиента для запросов в тесте
        url = reverse('shopapp:store_services')
        response = c.get(url)  # отправляем гет запрос на страницу сервиса
        self.assertEqual(response.status_code, 200)


class ProductCreateViewTestCase(TestCase):
    def setUp(self):
        self.product_name = "".join(choices(ascii_letters, k=10))  # генерируем случайную строку
        # удаляем из бд продукт с таким же именем
        Product.objects.filter(name=self.product_name).delete()

        # создаём суперпользователя (не берётся из базы, а создаётся в тестовой БД)
        self.user = User.objects.create_superuser(
            username="admin",
            password="uQ@m87ZRF6kELid",
            email="afrika8759116@gmail.com",
            first_name="Александр",
            last_name="Тананов",
        )
        # логинимся под этим пользователем
        self.client.login(username="admin", password="uQ@m87ZRF6kELid")

    def test_create_product(self):
        """

        """
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                "name": self.product_name,
                "description": "A good table",
                "price": "3000.23",
                "discount": "10"
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailViewTestCase(TestCase):
    """
    Класс тестов для проверки страницы продукта
    """
    @classmethod
    def setUpClass(cls):
        """
        подготовка данных перед тестом 1 раз для всех тестов в классе
        """
        faker = Faker()  # создаем экземпляр класса(генерация слов)
        cls.random_product_name = faker.word()  # случайное слово типа название продукта
        # создаем продукт в бд self.product - экземпляр продукта со всеми атрибутами
        cls.product = Product.objects.create(name=cls.random_product_name)

    @classmethod
    def tearDownClass(cls):
        """
        Очистка данных после теста в любом случае
        даже если тест упадет
        """
        Product.objects.filter(name=cls.random_product_name).delete()

    def test_get_product(self):
        """
        Тест проверяет, что страница деталей продукта (Product Detail)
        доступна по URL и возвращает HTTP статус 200 (успешный ответ).
        """
        response = self.client.get(
            reverse("shopapp:products_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        """
        Тест проверяет, что страница деталей продукта доступна и
        что на странице отображается название продукта.
        """
        response = self.client.get(
            reverse("shopapp:products_details", kwargs={"pk": self.product.pk})
        )
        # Проверяем, что HTTP-ответ успешный (по умолчанию assertContains проверяет это)
        # Проверяем, что на странице присутствует имя продукта
        self.assertContains(response, self.product.name)



class ProductsListViewTestCase(TestCase):
    """
    Класс тестов для проверки CBV (ProductsListView)
    """
    # fixtures указывает фикстуры — JSON-файлы с заранее подготовленными данными,
    # которые автоматически накатываются в тестовую базу перед запуском теста
    fixtures = [
        'full-fixture.json',  # фикстура со всеми данными, в том числе связанными
    ]

    def test_products(self):
        # создаём GET-запрос к представлению списка продуктов через тестовый клиент Django
        response = self.client.get(reverse('shopapp:products_list'))
        # assertQuerysetEqual сравнивает QuerySet с ожидаемым списком значений.
        # Здесь мы сравниваем QuerySet всех продуктов, которые не архивированы
        # с теми продуктами, которые вернуло представление (response.context["products"])
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),  # QuerySet или список объектов, который мы тестируем.
            values=[p.pk for p in response.context["products"]],  # список ожидаемых значений (например, PK, имена, словари и т.д.).
            transform=lambda product: product.pk,  # функция, которая применяется к каждому объекту QuerySet перед сравнением
        )

        # Здесь мы проверяем какой шаблон был использован
        self.assertTemplateUsed(response, 'shopapp/products-list.html')

class OrdersListViewTestCase(TestCase):
    """
    Класс тестов для проверки страницы списка заказов (OrdersListView)
    """

    @classmethod
    def setUpClass(cls):
        # Этот метод вызывается один раз перед всеми тестами класса
        # Создаем суперпользователя, которого будем использовать в тестах
        cls.user = User.objects.create_superuser(
            username="admin",  # имя пользователя
            password="uQ@m87ZRF6kELid",  # пароль
            email="afrika8759116@gmail.com",  # email
            first_name="Александр",  # имя
            last_name="Тананов",  # фамилия
        )

    @classmethod
    def tearDownClass(cls):
        # Этот метод вызывается один раз после всех тестов класса
        # Удаляем созданного суперпользователя, очищая тестовую БД
        cls.user.delete()

    def setUp(self):
        # Этот метод вызывается перед каждым отдельным тестом
        # Принудительно логиним пользователя в тестовом клиенте
        self.client.force_login(self.user)

    def test_orders_view(self):
        # Отправляем GET-запрос к представлению списка заказов
        response = self.client.get(reverse('shopapp:order_list'))
        # Проверяем, что в ответе содержится слово 'orders'
        # Это гарантирует, что страница успешно отобразилась и контент загружен
        self.assertContains(response, 'orders')

    def test_order_list_not_authenticated(self):
        # Разлогиниваем пользователя, чтобы проверить доступ неавторизованного юзера
        self.client.logout()
        # Отправляем GET-запрос к странице списка заказов
        response = self.client.get(reverse('shopapp:order_list'))
        # Проверяем, что ответ является редиректом (302), а не 200
        self.assertEqual(response.status_code, 302)
        # Проверяем, что редирект идет на страницу логина
        # `response.url` содержит полный URL редиректа, включая параметр next
        # `assertIn` проверяет, что базовая часть логина есть в URL
        self.assertIn(str(settings.LOGIN_URL), response.url)

class ProductsExportViewTestCase(TestCase):
    """
    TDD - test
    """
    fixtures = [
        'full-fixture.json',  # фикстура со всеми данными, в том числе связанными
    ]
    def test_get_products_view(self):
        # Тест будет сравнивать выгруженные данные с теми что лежат в бд
        response = self.client.get(
            reverse("shopapp:products-export"),
        )
        # проверяем что страница доступна статус код 200
        self.assertEqual(response.status_code, 200)
        # запрашиваем все продукты из бд отсортированные по pk списком

        # проверяем что объекты из базы реально есть
        print("Products count:", Product.objects.count())
        for p in Product.objects.all():
            print(p.pk, p.name, p.price, p.archived)

        products = Product.objects.order_by("pk").all()
        expected_data = [ # это Python list comprehension (генератор списка)
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived
            } # выражение
            for product in products # цикл, перебирает все продукты из базы
        ]
        # Получаем данные ответа в формате JSON
        # response.json() парсит JSON-строку в обычный Python словарь
        product_data = response.json()
        # Проверяем, что ключ 'products' в JSON содержит список продуктов,
        # который совпадает с тем, что есть в базе
        self.assertEqual(
            product_data["products"], # # ключ 'products' берётся из JSON
            expected_data # данные из базы (ожидаемый список продуктов
        )

class OrderDetailViewTestCase(TestCase):
    """
    Клас тестов для проверки view - OrderDetailView(PermissionRequiredMixin, DetailView)
    """
    @classmethod
    def setUpClass(cls):
        """
        Один раз перед всеми тестами создаем пользователя,
        добавляем ему разрешение (“shopapp.view_order”).
        """
        # создали юзера
        cls.user = User.objects.create_user(
            username="test_user",
            first_name="Александр",
            last_name="Тананов",
            email="t_afrika_777ne@mail.ru",
            is_staff=True,
            is_active=True,
            password="uQ@m87ZRF6kELid"
        )
        # получаем обьект права
        cls.permission = Permission.objects.get(
            codename="view_order"
        )
        # Добавляем пользователю право напрямую
        cls.user.user_permissions.add(cls.permission)
        # сохраняем изменение в пользователе
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        """
        удаляем пользователя поле всех тестов
        """
        cls.user.delete()

    def setUp(self):
        # логиним пользователя в сесии
        self.client.login(
            username=self.__class__.user.username,
            password="uQ@m87ZRF6kELid"
        )
        # создаем заказ для текущего пользователя
        self.order = Order.objects.create(
            delivery_address="Город Лаишево Улица Горького Дом 66А Квартира 17",
            promocode="zsdfg128764",
            user=self.__class__.user
        )
    def tearDown(self):
        # удаляем заказ после каждого теста
        self.order.delete()

    def test_order_detail(self):
        url = reverse(
            "shopapp:order_details",
            kwargs={"pk": self.order.pk}
        )
        response = self.client.get(url)
        # проверяем что в теле ответа есть адрес заказа
        self.assertContains(response, self.order.delivery_address)
        # проверяем, что в теле ответа есть промокод
        self.assertContains(response, self.order.promocode)
        # проверяем, что в контексте ответа тот же заказ, который был создан
        response_order = response.context['order'] # получаем данные заказа из контекста
        self.assertEqual(response_order.pk, self.order.pk)
        print("Тест из первой задачи:")
        print(f"\nДанные которые вы сравниваете в тесте,"
              f" то есть те которые сформировали из модели: {self.order}")
        print(f"\nДанные которые получили из запроса к endpoint'у': {response_order}")


class OrdersExportTestCase(TransactionTestCase):
    """
    класс тестов по заданию со звездочкой * (тест по TDD),
    выгрузка заказов в JSON
    """
    fixtures = [
        'user-fixtures.json',
        'products-fixtures.json',
        'orders-fixtures.json',
        'groups-fixture.json'
    ]

    @classmethod
    def setUpClass(cls):
        """
        Один раз перед всеми тестами создаем пользователя,
        делаем его is_staff=True (сотрудником).
        """
        # создали юзера сотрудника is_staff
        cls.user_is_staff = User.objects.create_user(
            id=9999999, # уникальный pk, чтобы избежать такой лютой головоебки
            username="is_staff_user",
            first_name="James",
            last_name="Bond",
            email="mi_six_666no@gmail.com",
            is_staff=True,
            is_active=True,
            password="uQ@m87ZRF6kELid"
        )

    @classmethod
    def tearDownClass(cls):
        """
        удаляем сотрудника после всех тестов
        """
        cls.user_is_staff.delete()

    def setUp(self):
        # Логиним сотрудника перед каждым тестом
        self.client.login(
            username=self.__class__.user_is_staff.username,
            password="uQ@m87ZRF6kELid"
        )

    def test_get_orders_list(self):
        """
        тест, который проверяет получение списка заказов:
        Статус кода-ответа — 200.
        В JSON-теле ответа должны быть ожидаемые значения.
        """
        # Делаем запрос на View
        response = self.client.get(
            reverse("shopapp:orders-export")
        )
        # проверяем что страница доступна статус код 200
        self.assertEqual(response.status_code, 200)
        # получаем данные из накатившейся с фикстур бд по заказам,
        # и связанным данным (пользователю, списку продуктов)
        orders = Order.objects.all()
        expected_data = [ # это Python list comprehension (генератор списка)
            {
                "pk": order.pk, # первичный ключ заказа
                "delivery_address": order.delivery_address, # Адрес заказа
                "promocode": order.promocode, # промокод заказа
                "created_at": order.created_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"), # дата создания заказа
                "user": order.user.id, # pk юзера сделавшего заказ
                "products": [product.pk for product in order.products.all()] # список pk - продуктов
            } # выражение
            for order in orders # цикл, перебирает все заказы из базы
        ]
        # Получаем данные ответа в формате JSON
        # response.json() парсит JSON-строку в обычный Python словарь
        order_data = response.json()
        self.assertEqual(order_data['orders'], expected_data)

        print(f"\nданные которые вы сравниваете в тесте, то есть те которые сформировали из модели: {expected_data}")
        print(f"\nданные которые получили из запроса к endpoint'у' {order_data['orders']}")
