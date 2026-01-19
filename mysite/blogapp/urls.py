from django.urls import path, include  # Для маршрутизации URL


from .views import ArticlesListView

app_name = "blogapp"



urlpatterns = [
    path('', ArticlesListView.as_view(), name="articles") # главная страница blogapp(со списком статей)
]