from .models import Article # импорт модели статья
from django.views.generic import ListView


class ArticlesListView(ListView):
    """
    Класс-представление для отображения списка статей (ListView).

    Основные особенности:
    - Использует модель Article для формирования списка объектов.
    - Шаблон для отображения: 'blogapp/article_list.html'.
    - Контекстная переменная для шаблона: 'articles'.
    - Оптимизация запросов к базе данных:
        * select_related('author', 'category') — подгружает связанные объекты
          ForeignKey (автора и категорию) в один SQL-запрос.
        * prefetch_related('tags') — подгружает связанные объекты ManyToManyField (теги)
          отдельным запросом, избегая N+1 проблемы.
        * (опционально) defer('content') — можно исключить поле content, если его
          не нужно загружать на странице, чтобы уменьшить объем передаваемых данных.
    - Позволяет эффективно отображать все статьи со всеми связанными сущностями,
      минимизируя количество SQL-запросов.

    Использование:
        При подключении URL, например path('articles/', ArticlesList.as_view(), name='articles_list'),
        шаблон получит в контексте переменную 'articles', с которой можно работать через цикл.
    """
    template_name = 'blogapp/article_list.html' # Указываем путь к HTML-шаблону
    context_object_name = "articles" # Имя переменной, под которым список объектов будет доступен в шаблоне.
    queryset = (Article
                .objects.select_related('author', 'category') # в один запрос подгружаем связные данные (автора и категории)
                .prefetch_related('tags') # дополнительным запросом подгружаем связные данные (теги статьи)
                .defer('content') # исключаем из подгрузки неиспользуемое поле content
                )


