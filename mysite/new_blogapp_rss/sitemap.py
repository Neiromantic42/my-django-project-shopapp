from django.contrib.sitemaps import Sitemap
from rest_framework.reverse import reverse

# Базовый класс Django для создания sitemap (карты сайта)

from .models import Article
# Импортируем модель статей, страницы которых попадут в sitemap


class BlogSitemap(Sitemap):
    """
    Sitemap для блога.

    Отвечает за генерацию списка URL опубликованных статей,
    которые будут добавлены в sitemap.xml.
    """

    changefreq = "never" # Подсказка поисковику: страницы статей редко меняются
    priority = 0.5 # Средний приоритет страницы в sitemap

    def items(self):
        """
        Возвращает queryset объектов,
        на основе которых будут сгенерированы URL в sitemap.
        """
        # Берём только опубликованные статьи
        return Article.objects.filter(published_at__isnull=False).order_by("-published_at")
        # Сортируем по дате публикации (сначала новые)

    def lastmod(self, obj: Article):
        """
        Возвращает дату последнего изменения страницы
        для sitemap.
        """
        return obj.published_at
