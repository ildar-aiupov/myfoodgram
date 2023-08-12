## Проект Foodgram

Foodgram - многопользовательский продуктовый помощник с базой кулинарных рецептов. Позволяет просматривать, публиковать, редактировать рецепты, сохранять в избранное, а также формировать и скачивать список покупок для выбранных рецептов. Зарегистрированные пользователи могут подписываться на других авторов.
Проект доступен по адресу [https://myfoodgram.didns.ru](https://myfoodgram.didns.ru).
Технически, в двух словах, сайт представляет собой фронтенд на REACT, который через API (DRF) взаимодействует с бэкендом на Django.

### Автор АПИ/бэкенда:

Ильдар Аюпов, 2023 г., e-mail: ildarbon@gmail.com, Telegramm: @ildarbonn

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

- Переименовать файл .env.example (настройки Джанго и подключения к базе данных) в корне проекта в файл .env. Данные настройки приведены для примера, они не соответствуют реальным настройкам сайта в продакшене, но их достаточно, чтобы можно было запустить проект на локальной машине. При желании, можно задать собственные настройки, отредактировав этот файл. Команда для переименования следующая:
```
mv .env.example .env
```

- Находясь в корневой папке проекта, запустить его сборку:
```
sudo docker compose up -d
```

- После успешной сборки создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

- Зайти в админ-панель через учетную запись созданного суперпользователя и создать один или несколько тэгов. После этого открыть проект.
```
Главная страница проекта: http://localhost:8000/

Админ-панель: http://localhost:8000/admin/

Техническая документация: http://localhost:8000/docs/
```

- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```
