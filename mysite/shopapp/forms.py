# Тут будут описаны все формы для использования в данном приложении
from django import forms  # Импортируем модуль forms из Django для работы с формами
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core import validators
from .models import Product, Order


class ProductForm(forms.ModelForm):  # создаём форму на основе модели Product
    """
    Форма для создания продукта с доп валидацией данных со скидкой
    """
    class Meta:  # внутренний класс с настройками формы
        model = Product  # указываем, с какой моделью связана форма
        fields = "name", "description", "price", "discount", "preview"  # перечисляем поля, которые будут в форме


    def clean(self):  # переопределяем метод clean для дополнительной валидации данных формы
        cleaned_data = super().clean()  # получаем уже очищенные (валидированные) данные из родительского класса
        price = cleaned_data.get("price")  # извлекаем значение цены из данных формы
        discount = cleaned_data.get("discount")  # извлекаем значение скидки из данных формы
        print("PRICE:", price, "DISCOUNT:", discount)  # для отладки: выводим цену и скидку в консоль
        if price is not None and discount is not None:  # проверяем, что оба значения указаны
            if price <= 3000 and discount > 0:  # если цена ≤ 3000, а скидка больше 0 —
                raise ValidationError(  # — вызываем ошибку валидации
                    "Скидка доступна только товарам дороже 3 000 рублей!"  # текст ошибки для пользователя
                )
        return cleaned_data  # возвращаем очищенные и проверенные данные формы


class OrderForm(forms.ModelForm):
    """
    Форма для создания заказа
    """
    class Meta:
        model = Order  # модель, на основе которой строится форма
        fields = ["delivery_address", "promocode", "products", "user"]  # поля формы, которые будут отображены
        exclude = ["created_at"]  # исключаем поле created_at из формы (оно задаётся автоматически)
        widgets = {
            "products": forms.CheckboxSelectMultiple(),  # отображаем поле products в виде множества чекбоксов
        }

    delivery_address = forms.CharField(
        label="Order address",
        help_text="Укажите город, улицу, номер дома и индекс",
        widget=forms.Textarea(attrs={"cols": 40, "rows": 5}),
        validators= [validators.RegexValidator(
            regex=r"(?i)город\s+[А-Яа-я]+\s+улица\s+[А-Яа-я]+"
                  r"\s+дом\s+\d{1,3}[А-Яа-я]?\s+квартира\s+\d{1,3}",
            message="Адрес должен быть в формате:"
                    " Город Москва Улица Пушкина Дом 66А Квартира 17"
        )]
    )

class GroupForm(forms.ModelForm):  # создаём форму, основанную на модели Group
    """
    Форма для создания новой группы
    """
    class Meta:  # внутренний класс с настройками формы
        model = Group  # указываем, с какой моделью связана форма
        fields = ["name"]  # определяем, какие поля из модели будут отображаться в форме


class CSVImportForm(forms.Form):
    """
    класс - форма для импорта данных через шаблон
    """
    csv_file = forms.FileField()
    # поле формы для загрузки файла; браузер покажет кнопку "Выберите файл"

class FileImportForm(forms.Form):
    """
    класс - форма для импорта данных через шаблон
    """
    file = forms.FileField()
    # поле формы для загрузки файла; браузер покажет кнопку "Выберите файл"