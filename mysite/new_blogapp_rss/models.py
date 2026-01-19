from django.db import models
from django.urls import reverse


class Article(models.Model):
    """
    класс - модель: Статья

    """
    title = models.CharField(max_length=100)
    body = models.TextField(null=True, blank=True) # Поле модет быть пустым(null=True), при заполнении через форму тоже( blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self) -> str:
        """
        Возвращает ссылку на конкретную статью.
        """
        return reverse("new_blogapp_rss:article", kwargs={"pk": self.pk})

