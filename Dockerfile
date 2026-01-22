# указываем версию пайтон(берём ту же версию Python, что и в проекте)
FROM python:3.12

# отключает буферизацию вывода Python, чтобы логи сразу писались в stdout/stderr
ENV PYTHONUNBUFFERED=1

# Создаем директорию в которой будем работать
WORKDIR /app

# Обновляем pip внутри контейнера до актуальной версии
RUN pip install --upgrade pip "poetry==2.3.1"

# Настраиваем Poetry так, чтобы не создавалось виртуальное окружение внутри контейнера
# зависимости будут установлены глобально в контейнере
RUN poetry config virtualenvs.create false --local

# Копируем файлы управления зависимостями Poetry (pyproject.toml и poetry.lock) в контейнер
COPY pyproject.toml poetry.lock ./

# Устанавливаем все зависимости проекта через Poetry
RUN poetry install --no-root

# копируем весь джанго проект mysite(где лежат все приложения проекта) в(.) - текущую директорию
COPY mysite .

# команда для запуска приложения внутри контейнера
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]




