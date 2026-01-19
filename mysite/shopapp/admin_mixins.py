import csv
# стандартный модуль Python для работы с CSV-файлами (чтение/запись)
from django.db.models.options import Options
# класс Options — это мета-информация о модели (через model._meta можно получить имя модели,
# список её полей, название таблицы и т.п.)
from django.db.models import QuerySet
# тип данных для queryset — набора объектов, возвращаемых запросами к БД
from django.http import HttpRequest, HttpResponse
# HttpRequest — объект запроса (кто вызвал action, какие данные пришли)
# HttpResponse — объект ответа (мы вернём CSV-файл как ответ браузеру)


class ExportAsCsvMixin:
    """
    Класс-примесь (mixin), который добавляет возможность экспорта данных в CSV.
    Примесь подключается к ModelAdmin и расширяет его функционал.
    """
    def export_csv(self, request: HttpRequest, queryset: QuerySet):
        """
        Метод, который будет превращать выбранные объекты админки в CSV
        и отдавать файл пользователю.
        """
        meta: Options = self.model._meta  # получаем мета-информацию модели (поля, имя и т.д.)

        field_name = [field.name for field in meta.fields]  # список имён всех полей модели для заголовков CSV

        response = HttpResponse(content_type="text/csv")  # создаём HTTP-ответ с типом CSV

        response["Content-Disposition"] = f"attachment; filename={meta}-export.csv"  # заставляем браузер скачать файл с именем

        csv_writer = csv.writer(response)  # создаём CSV-писатель для записи в response.

        csv_writer.writerow(field_name)  # записываем первую строку — заголовки колонок

        for obj in queryset:  # перебираем все выбранные объекты
            csv_writer.writerow(
                [getattr(obj, field) for field in field_name]
            )  # записываем значения полей объекта как строку CSV

        return response  # возвращаем сформированный CSV-файл пользователю

    export_csv.short_description = "Export as CSV"  # описание метода для админки