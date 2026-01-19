from django.urls import path, include  # Для маршрутизации URL


from .views import (
    ArticlesListView,
    ArticleDetailView,
    LatestArticlesFeed,
)

app_name = "new_blogapp_rss" # пространство имен приложения, для генерации ссылок итд



urlpatterns = [
    path("articles/", ArticlesListView.as_view(), name="articles"), # Путь ко всем статьям
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article"), # Путь к конкретной статье
    path("articles/latest/feed/", LatestArticlesFeed(), name="articles-feed"), # Путь к ленте новостей

]