## Проект Foodgram

Foodgram - многопользовательский продуктовый помощник с базой кулинарных рецептов. Позволяет просматривать, публиковать, редактировать рецепты, сохранять в избранное, а также формировать и скачивать список покупок для выбранных рецептов. Зарегистрированные пользователи могут подписываться на других авторов.
Проект доступен по адресу [https://myfoodgram.didns.ru](https://myfoodgram.didns.ru).
Технически в двух словах сайт представляет собой фронтенд на REACT, который через API взаимодействует с бэкендом на Django.

### Автор АПИ/бэкенда:

Ильдар Аюпов, 2023 г.

### Основные библиотеки и технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Continuous Integration, Continuous Deployment, Djoser

### Развернуть проект на локальной машине:

- Установить Docker, Docker Compose:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

- Клонировать репозиторий:
```
git clone git@github.com:ildar-aiupov/myfoodgram.git
```

- При желании, можно задать собственные настройки Джанго и подключения к базе данных. Для этого в корневой папке проекта создать файл .env и заполнить своими данными по образцу ниже. Если не будут заданы настройки, то проект запустится с настройками по умолчанию:
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=qwerty
DEBUG=False
ALLOWED_HOSTS=*
```

- Находясь в корневой папке проекта, запустить его:
```
sudo docker compose up -d
```

- После успешной установки создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```

- После запуска проект будут доступен по адресу: [http://localhost:8000/](http://localhost:8000/)
```
Админ панель: /admin/
Техническая документация: /api/docs/
```
