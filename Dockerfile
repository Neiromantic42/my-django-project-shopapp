# указываем версию пайтон(берём ту же версию Python, что и в проекте)
FROM python:3.12

# отключает буферизацию вывода Python, чтобы логи сразу писались в stdout/stderr
ENV PYTHONUNBUFFERED=1

# Создаем директорию в которой будем работать
WORKDIR /app

# копируем зависимости с хостовой ммашины(с той машины где идет разработка приложения)
COPY mysite/requirements.txt requirements.txt

# Обновляем pip внутри контейнера до актуальной версии
RUN pip install --upgrade pip

# Устанавливаем Python-зависимости проекта из файла requirements.txt
RUN pip install -r requirements.txt

# копируем весь джанго проект mysite(где лежат все приложения проекта) в(.) - текущую директорию
COPY mysite .

# команда для запуска приложения внутри контейнера
CMD ["python", "manage.py", "runserver"]




