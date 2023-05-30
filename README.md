# Foodgram

 Продуктовый помощник - дипломный проект курса Backend-разработки Яндекс.Практикум. Проект представляет собой онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект реализован на `Django` и `DjangoRestFramework`. Доступ к данным реализован через API-интерфейс. Документация к API написана с использованием `Redoc`.

Айпи адрес сайта: http://158.160.107.155/

## Технологии:
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org)
- [Docker](https://www.docker.com)
- [Docker-compose](https://docs.docker.com/compose/)
- [PosgreSQL](https://www.postgresql.org)
- [Nginx](https://nginx.org/)
- [Gunicorn](https://gunicorn.org)

## Установка и развертывание проекта:
- Клонировать репозиторий
- Создать виртуальное окружение и установить зависимости из requirements.txt
- Установить Docker и docker-compose
- Забилдить и поднять проект:
```
$ docker-compose up -d --build 
```
- Выполнить команды для миграции, создания суперюзера и сбора статики:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
- Загрузить список ингредиентов из csv файла:
```
docker-compose exec web python manage.py upload
```

### Пример наполнения env файла
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres (your password)
DB_HOST=db
DB_PORT=5432