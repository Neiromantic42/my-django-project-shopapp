from django.test import Client
from django.test import Client  # Импорт тестового клиента для HTTP-запросов
import json  # Модуль для работы с JSON (чтобы декодировать ответ)
from django.test import TestCase  # Базовый класс для тестов с БД
from django.urls import reverse  # Позволяет получить URL по имени маршрута

class GetCookieView(TestCase):
    """
    Тест функции get_cookie_view —
    проверяет, что страница для получения cookie работает корректно
    """
    def test_get_cookie_view(self):
        client = Client()  # Создаём объект тестового клиента
        url = reverse('myauth:cookie-get')  # Получаем URL по имени маршрута "cookie-get"
        response = client.get(url)  # Отправляем GET-запрос на этот URL
        self.assertEqual(response.status_code, 200)  # Проверяем, что страница вернула HTTP 200 (OK)
        self.assertContains(response, 'Cookie value')  # Проверяем, что в HTML-ответе есть строка "Cookie value"

class FooBarViewTest(TestCase):
    """
    Тест CBV FooBarView —
    проверяет, что возвращается корректный JSON-ответ и правильный тип контента
    """
    def test_foo_bar_view(self):
        response = self.client.get(reverse('myauth:foo-bar'))  # Отправляем GET-запрос через self.client (встроенный клиент TestCase)
        self.assertEqual(response.status_code, 200)  # Проверяем, что ответ успешный (HTTP 200)
        self.assertEqual(  # Проверяем заголовок Content-Type
            response.headers['content-type'], 'application/json'
        )
        expected_data = {"foo": "bar", "spam": "eggs"}  # Это ожидаемые данные (что view должна вернуть)
        # received_data = json.loads(response.content)  # Преобразуем тело ответа (JSON-строку) в Python-словарь
        # self.assertEqual(received_data, expected_data)  # Проверяем, что полученные данные совпадают с ожидаемыми
        self.assertJSONEqual(response.content, expected_data) # Проверка вернувшегося json ответа, аналогично 2 строкам выше
