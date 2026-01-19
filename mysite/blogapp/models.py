from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    """
    Класс - модель представляет автора статьи.

    Она имеет 2 поля:
        - name (имя автора)
        - bio (биография автора)
    """

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    name = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self) -> str:
        return f"Author: {self.name}"


class Category(models.Model):
    """
    класс - модель представляет категорию статьи.

    Она имеет одно поле:
        - name (название категории)
    """

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    name = models.CharField(max_length=40)

    def __str__(self) -> str:
        return f"Category: {self.name}"


class Tag(models.Model):
    """
    класс - модель представляет тэг который можно назначить статье.

    Она имеет одно поле:
        - name (название тега)
    """

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"Tag: {self.name}"


class Article(models.Model):
    """
    класс - модель представляет статью.

    Она имеет следующие поля:
        - title (заголовок статьи)
        - content (содержимое статьи)
        - pub_date (дата публикации статьи)
        - author (автор статьи, связь многие к одному с моделью - Author)
        - category (категория статьи, связь многие к одному с моделью - Category)
        - tags (тэги статьи, связь многие ко многим с моделью Tag)
    """

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="articles")

    def __str__(self) -> str:
        return f"Title: {self.title}"
