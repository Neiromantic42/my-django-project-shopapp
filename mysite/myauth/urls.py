from django.contrib.auth.views import LoginView  # LoginView — встроенное представление для логина
from django.urls import path  # path — функция для задания маршрутов URL

from .views import ( # Импортируем из текущего пакета (текущей директории) файл views.py
    get_cookie_view, # Функция для чтения значения cookie из запроса
    set_cookie_view, # Функция для установки cookie в ответ
    set_session_view, # Функция для записи данных в сессию
    get_session_view, # Функция для чтения данных из сессии
    logout_view, # Функция для выхода пользователя из сессии (разлогинивания)
    MyLogoutView, # Класс-представление для выхода пользователя из системы.
    AboutMeView, # Класс-представление показа информации о пользователе
    RegisterView, # Класс-представление для регистрации пользователя
    FooBarView, # Класс-представление просто дял тестов
    UsersListView, # Класс-представление для страницы всех пользователей
    UserDetailView, # Класс-представление для показа деталей конкретного пользователя
    ProfileUpdateView, # Класс-представление для обновления профиля
    HelloView  # Класс-представление для демонстрации локализации\интернационализации
)

app_name = "myauth"  # Пространство имён приложения

urlpatterns = [  # Список маршрутов приложения
    path(
        "login/",  # URL страницы логина
        LoginView.as_view(  # Используем стандартный LoginView
            template_name="myauth/login.html",  # Шаблон формы логина/имя шаблона
            redirect_authenticated_user=True,  # переадресация аутентифицированного пользователя
            next_page="myauth:about-my"  # Опционально: куда редиректить после логина (переопределяет LOGIN_REDIRECT_URL)
        ),
        name="login",  # Имя маршрута для {% url %}
    ),
    path("register/", RegisterView.as_view(), name="register"),  # маршрут для удаления данных сессии\разлогинься
    path("logout/", MyLogoutView.as_view(), name="logout"),  # маршрут для удаления данных сессии\разлогинься
    path("about-my/", AboutMeView.as_view(), name="about-my"),  # маршрут для показа информации о пользователе
    path("users-page/", UsersListView.as_view(), name="users-page"), # маршрут для показа информации о всех юзерах
    path("user/<int:pk>/", UserDetailView.as_view(), name="user-detail"), # маршрут для показа конкретного юзера

    path("profile-update/<int:pk>", ProfileUpdateView.as_view(), name="profile-update"), # маршрут для обновления профиля

    path("cookie/get", get_cookie_view, name="cookie-get"),  # маршрут для чтения куки
    path("cookie/set", set_cookie_view, name="cookie-set"),  # маршрут для установки куки

    path("session/set", set_session_view, name="session-set"),  # маршрут для установки данных сессии
    path("session/get", get_session_view, name="session-get"),  # маршрут для чтения данных сессии

    path("foo-bar", FooBarView.as_view(), name="foo-bar"), # маршрут для теста
    path("hello/", HelloView.as_view(), name='hello'), # маршрут для демонстрации работы представления с локализацией, интернационализацией и плюреализацией
]  # Конец списка маршрутов