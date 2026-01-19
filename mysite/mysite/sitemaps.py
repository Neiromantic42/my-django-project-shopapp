from new_blogapp_rss.sitemap import BlogSitemap
# Импортируем класс sitemap для блога
from shopapp.sitemap import ShopappSitemap

# Django использует этот словарь для генерации sitemap.xml
sitemaps = {
    "new_blogapp": BlogSitemap, # Регистрируем sitemap под именем new_blogapp
    "shop": ShopappSitemap, # Регистрируем sitemap под именем shopapp
}