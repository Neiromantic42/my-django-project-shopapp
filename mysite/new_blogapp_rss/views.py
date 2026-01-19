from django.contrib.syndication.views import Feed
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse

from .models import Article


class ArticlesListView(ListView):
    """
    Класс - представление

    Для отображения всех статей
    """
    queryset = (
        Article.objects
        .filter(published_at__isnull=False) # Берём только опубликованные статьи (дата публикации задана)
        .order_by("-published_at") # сортировка чтобы самые новые статьи были выше всех в представлении пользователю
    )
    context_object_name = 'articles'

class ArticleDetailView(DetailView):
    """
    Класс - представление

    Для отображения одной конкретной статьи
    """
    model = Article # просто указываем модель с которой работаем, qs по pk выполнится под капотом
    context_object_name = 'article'



class LatestArticlesFeed(Feed):
    """
    Класс-представление (RSS) для ленты новостей.

    RSS лента позволяет подписчикам получать последние статьи автоматически.
    """
    title = "Blog articles (latest)" # Заголовок для rss-ленты
    description = "Update on changes and addition blog articles" # Описание ленты
    link = reverse_lazy("new_blogapp_rss:articles") # Ссылка на страницу со списком статей

    def items(self):
        """
        Метод возвращает список объектов, которые будут включены в RSS-ленту.

        Каждый объект будет обрабатываться методами item_title, item_description и item_link.
        """
        return (
            Article.objects
            .filter(published_at__isnull=False)
            .order_by("-published_at")[:5] # срез берет только первые 5 статей
        )

    def item_title(self, item: Article):
        """
        Метод формирует заголовок для каждого элемента RSS-ленты.

        Django вызывает этот метод для каждого объекта из items().
        """
        return item.title  # Заголовок конкретной статьи

    def item_description(
            self,
            item: Article # один элемент из items()
    ):
        """
        Метод формирует описание статьи
        """
        return item.body[:200] # Возвращаем срез из статьи в 200 символов

    def item_link(self, item: Article) -> str:
        """
        Возвращает ссылку на конкретную статью для RSS (<link>).
        """
        return reverse("new_blogapp_rss:article", kwargs={"pk": item.pk})  # строим URL по имени маршрута и pk