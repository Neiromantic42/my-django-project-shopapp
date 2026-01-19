from django.contrib.sitemaps import Sitemap

from shopapp.models import Product
# Импортируем модель товаров, страницы которых попадут в sitemap


class ShopappSitemap(Sitemap):
    """
    Sitemap для магазина.

    Отвечает за генерацию списка URL товаров,
    которые будут добавлены в sitemap.xml.
    """
    changefreq = "never" # Подсказка поисковику: страницы статей редко меняются
    priority = 0.5 # Средний приоритет страницы в sitemap

    def items(self):
        """
        Возвращает queryset объектов,

        на основе которых будут сгенерированы URL в sitemap.
        """
        # Возвращаем объекты товаров (не архивированные) в порядке их создания (сперва новые)
        return Product.objects.filter(archived=False).order_by("-created_at")

    def lastmod(self, obj: Product):
        """
        Возвращает дату последнего изменения для sitemap.
        """
        return obj.created_at # используем created_at как дату изменения