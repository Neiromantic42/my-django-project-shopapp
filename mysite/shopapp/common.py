import json
from csv import DictReader         # читаем CSV как словари
from io import TextIOWrapper       # преобразуем бинарный файл в текстовый поток

from django.db import transaction  # для атомарных операций с базой

from shopapp.models import Product, Order
from django.contrib.auth.models import User  # импорт модели пользователя Django

import logging

logger = logging.getLogger(__name__)


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(       # оборачиваем файл в текстовый поток с нужной кодировкой
        file,
        encoding,
    )
    reader = DictReader(csv_file)   # читаем CSV построчно, каждая строка — словарь

    product = [
        Product(**row)              # создаём объект Product из каждой строки CSV
        for row in reader
    ]
    with transaction.atomic():      # вся операция выполняется как единая транзакция
        Product.objects.bulk_create(product, batch_size=50)  # создаём все объекты за один запрос (партиями по 50)
    return product                  # возвращаем список созданных объектов


def save_file_orders(file, encoding):
    wrapped_file = TextIOWrapper( # оборачиваем файл в текстовый поток с нужной кодировкой
        file,
        encoding,
    )
    orders = json.load(wrapped_file)
    # logger.info("Содержимое загруженного файла: %s", orders)
    for o in orders:
        user = User.objects.get(pk=o['user_id'])
        order = Order.objects.create(
            delivery_address=o["delivery_address"],
            promocode=o["promocode"],
            created_at=o["created_at"],
            user_id=o["user_id"]
        )
        products = Product.objects.filter(pk__in=o["product_ids"])

        order.products.set(products)
