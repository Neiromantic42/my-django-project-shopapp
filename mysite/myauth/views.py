from random import random # Импорт декоратора для кеширования отдельных представлений (Views)
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import (  # импортируем декораторы для защиты представлений:
    login_required,  # login_required — требует, чтобы пользователь был авторизован,
    permission_required,  # permission_required — требует наличия у пользователя указанного права (permission) для доступа к вью.
    user_passes_test  # user_passes_test - Позволяет задать собственную функцию проверки (test_func),
    # которая возвращает True, если доступ разрешён, и False — если нет.
)
from django.contrib.auth.mixins import (  # Миксины для ограничения доступа к класс-представлениям (views).
    UserPassesTestMixin  # Позволяет задать собственную функцию проверки (test_func),
    # которая возвращает True, если доступ разрешён, и False — если нет.
)
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    TemplateView,  # Показывает обычную страницу (HTML) — без логики сохранения данных.
    CreateView,  # Создаёт новую запись в базе (например, нового пользователя или продукт).
    FormView,  # Показывает любую форму и обрабатывает её, но сам по себе ничего не сохраняет.
    UpdateView,  # Редактирует (обновляет) существующую запись в базе.
    ListView,  # Показывает список объектов (список пользователей, товаров, заказов).
    DetailView,  # Показывает подробно один объект (страница одного пользователя или товара).
)
from django.utils.translation import gettext as _  # обычный перевод
from django.utils.translation import gettext_lazy as _  # ленивый перевод
from django.utils.translation import ngettext # множественные формы


from .models import Profile  # Импортируем модель профиля пользователя (расширение стандартного User)
from .forms import ProfileForm


import logging
log = logging.getLogger(__name__)

class HelloView(View):
    welcome_message = _("welcome hello world")

    def get(self, request: HttpRequest) -> HttpResponse:
        # количество товаров из GET-параметра
        items_str = request.GET.get('items') or 0
        items = int(items_str)

        # множественная форма для продуктов
        product_line = ngettext(
            "one product",  # singular — форма для 1 предмета
            "{count} product",  # plural — форма для многих предметов
            number=items,  # число, на основании которого выбирается форма
        ).format(count=items)  # подстановка числа в строку

        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{product_line}</h2>"
        )


class RegisterView(CreateView):
    """
    Класс-представление для создания нового пользователя
    на основе формы UserCreationForm
    """
    form_class = UserCreationForm  # Указываем форму, с которой будем работать.
    # UserCreationForm — встроенная Django форма для регистрации, проверяет username и пароль
    template_name = "myauth/register.html"  # Имя шаблона, который будет рендерить страницу регистрации
    success_url = reverse_lazy(
        "myauth:about-my")  # URL, на который перенаправим пользователя после успешной регистрации

    def form_valid(self, form):
        # Этот метод вызывается, если форма прошла валидацию (все поля корректны)
        response = super().form_valid(form)
        # Вызываем родительский form_valid:
        # 1) сохраняет объект пользователя в базу (self.object = form.save())
        # 2) возвращает редирект на success_url
        Profile.objects.create(user=self.object)  # После регистрации создаем профиль текущему пользователю
        username = form.cleaned_data.get('username')
        # Из формы получаем валидированный username, который ввёл пользователь
        password = form.cleaned_data.get('password2')
        # Из формы получаем второй пароль (подтверждение), потому что UserCreationForm использует password2 для проверки
        user = authenticate(  # Получаем обьект User если успех иначе None
            self.request,  # Передаём объект запроса, чтобы Django мог работать с сессией и бекэндом аутентификации
            username=username,  # Имя пользователя, введённое и валидированное из формы
            password=password  # пароль пользователя, введённый и проверенный в форме
        )
        login(request=self.request, user=user)  # Логиним пользователя в текущую сессию
        return response


class AboutMeView(FormView):
    """
    Класс-представление для отображения информации о вошедшем пользователе
    и возможности менять аватарку через форму.
    """
    form_class = ProfileForm  # Форма для редактирования профиля (аватар)
    template_name = "myauth/about-me.html"  # Шаблон, где показываем форму и данные пользователя
    success_url = reverse_lazy("myauth:about-my")  # URL, на который редирект после успешного сохранения формы

    def form_valid(self, form):
        # Получаем существующий профиль пользователя (если есть)
        profile = getattr(self.request.user, "profile", None)
        # Создаём новую форму ProfileForm с данными из POST и загруженных файлов,
        # и привязываем её к существующему профилю через instance
        if profile is None:  # если профиль еще не создан
            profile = form.save(commit=False)  # создаем профиль
            profile.user = self.request.user  # привязываем текущему профилю юзера
            profile.save()  # сохраняем профиль в бд
        else:
            form = ProfileForm(
                self.request.POST,  # Данные формы из запроса (текстовые поля)
                self.request.FILES,  # Загруженные файлы (например avatar)
                instance=profile  # Если профиль существует, форма редактирует его; если нет — None
            )
            form.save()  # Сохраняем изменения в базе (и загруженный файл сохраняется в MEDIA_ROOT)
        return super().form_valid(form)  # Вызываем родительский метод: редирект на success_url


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    """
    класс представление для редактирования профиля
    """
    form_class = ProfileForm
    model = Profile
    template_name = 'myauth/profile-update.html'
    context_object_name = "profile"

    def get_success_url(self):
        return reverse(
            "myauth:user-detail",
            kwargs={"pk": self.object.user.pk}
        )

    def test_func(self):
        profile = self.get_object()
        return self.request.user.is_staff or self.request.user == profile.user


class UserDetailView(DetailView):
    """
    Класс-представление для страницы деталей юзера
    """
    template_name = 'myauth/user-detail.html'
    model = User
    context_object_name = "user"


class UsersListView(ListView):
    """
    клас представление для вывода списка пользователей
    """
    template_name = "myauth/users-list.html"  # путь к шаблону, который будет рендериться
    model = User  # модель, из которой берём данные (все пользователи)
    context_object_name = 'users'  # имя переменной в шаблоне (будет доступна как users)


def login_view(request: HttpRequest) -> HttpResponse:  # Представление для страницы логина, получает объект запроса
    """
    вью функция для рендеринга формы аутентификации пользователя
    """
    if request.method == "GET":  # Если запрос GET — показываем форму
        if request.user.is_authenticated:  # Проверяем, залогинен ли пользователь
            return redirect('/admin')  # Если да, перенаправляем его на /admin

        return render(request, 'myauth/login.html')  # Если нет, рендерим страницу логина

    # Если запрос POST — пользователь отправил форму
    username = request.POST['username']  # Берём введённый username из данных формы
    password = request.POST['password']  # Берём введённый пароль из данных формы

    user = authenticate(request, username=username, password=password)
    # Проверяем подлинность пользователя: есть ли такой username и совпадает ли пароль
    # Если есть — вернётся объект User, если нет — None

    if user is not None:  # Если аутентификация успешна
        login(request, user)  # Входим в систему: сохраняем пользователя в сессии
        return redirect('/admin')  # Перенаправляем на /admin

    return render(request, 'myauth/login.html', {"error": "Invalid login credentials"})


def logout_view(request: HttpRequest):  # Функция-представление, принимающая объект запроса от пользователя
    """
    Логаут - функция служит для разлогинивания пользователя в сесии
    """
    logout(request)  # Удаляет данные сессии и "разлогинивает" пользователя
    return redirect(
        reverse("myauth:login"))  # Перенаправляет пользователя на страницу входа по имени маршрута 'myauth:login'


class MyLogoutView(LogoutView):  # Определяем собственный класс представления, наследуя поведение LogoutView
    """
    Класс-представление для выхода пользователя из системы.
    После выхода перенаправляет на страницу входа 'myauth:login'.
    """
    http_method_names = ['get', 'post']
    next_page = reverse_lazy(
        "myauth:login" # После успешного выхода пользователь будет перенаправлен на страницу логина
    )

    def get(self, request, *args, **kwargs):
        logout(request) # явно вызываем разлогинивание
        return redirect(self.next_page)


@user_passes_test(lambda user: user.is_superuser)
# @user_passes_test:
# Декоратор проверяет, выполняется ли заданное условие для пользователя.
# В нашем случае: lambda user: user.is_superuser
# - user — текущий пользователь (request.user)
# - user.is_superuser — возвращает True, если пользователь является суперюзером
# Если условие True — функция выполняется, если False — будет редирект на страницу логина
# Можно использовать raise_exception=True для генерации PermissionDenied вместо редиректа.
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    """
    Устанавливает куку 'fizz' со значением 'buzz' на 1 час.
    Возвращает простой HTTP-ответ с текстом.
    """
    response = HttpResponse("Cookie set")  # создаём ответ с текстом
    response.set_cookie("fizz", "buzz", max_age=3600)  # добавляем куку на 1 час
    return response  # возвращаем ответ клиенту

@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    """
    Читает куку 'fizz' из запроса.
    Если куки нет, возвращает 'default value'.
    Возвращает текстовое значение куки в HTTP-ответе.
    """
    value = request.COOKIES.get("fizz", "default value")  # получаем значение куки\если нет устанавливаем дефолтное знач
    return HttpResponse(f"Cookie value: {value!r} + {random()}")  # возвращаем значение куки в ответе


@permission_required("myauth.view_profile", raise_exception=True)
# Декоратор защищает функцию вью: доступ разрешён только пользователям с правом "view_profile" для приложения myauth.
# Параметр raise_exception=True говорит: если пользователь не имеет права, не перенаправлять на страницу логина,
# а сразу вызвать исключение PermissionDenied (HTTP 403).
def set_session_view(request: HttpRequest) -> HttpResponse:
    """
    Устанавливает в сессии пользователя ключ 'foobar' со значением 'spameggs'.
    Возвращает HTTP-ответ с текстом подтверждения.
    """
    request.session["foobar"] = "spameggs"  # сохраняем данные в сессии пользователя
    return HttpResponse("Session set!")  # возвращаем простой текстовый ответ клиенту


@login_required  # декоратор — разрешает доступ только авторизованным пользователям
def get_session_view(request: HttpRequest) -> HttpResponse:
    """
    Читает значение 'foobar' из сессии пользователя.
    Если такого ключа нет, возвращает 'default'.
    Возвращает текстовое значение сессии в HTTP-ответе.
    """
    value = request.session.get("foobar", "default")  # получаем значение из сессии, если нет — "default"
    return HttpResponse(f"Session value: {value!r}")  # возвращаем значение сессии в ответе


class FooBarView(View):
    """
    Просто CBV для теста -> теста! :))
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
