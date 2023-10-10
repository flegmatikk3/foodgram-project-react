# Foodgram
Фудграм является продуктовым помощником. Позволяет добавлять свои рецепты, подписываться на авторов рецептов, добавлять в избранное то, что хочется приготовить в будущем, а так же добавлять в корзину все рецепты, которые понравились, а потом автоматически подсчитать необходимые ингридиентны и составить продуктовую корзину для похода в магазин!

Проект доступен по ссылке : https://foodgram-fuck-your-mum.ru/

Создана админка с логином: ai@mail.ru и паролем 1123455A

--------
## Технологии
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
--------
## Использование
Необходимо клонировать репозиторий:
```
git clone git@github.com:flegmatikk3/foodgram-project-react.git
```

Установить на сервере докер

Скопировать на сервер файлы компоуза и конфиг nginx из папки infra
```
scp docker-compose.yml nginx.conf username@IP:/home/username/ 
```

В Github Actions прописать секреты:
```
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
PASSPHRASE
SSH_KEY
TELEGRAM_TO
TELEGRAM_TOKEN
USER
```

Так же в папку infra на сервере перенести .env файл, в котором необходимо задать переменные окружения
```
POSTGRES_USER=django_user
POSTGRES_DB=django
POSTGRES_PASSWORD=yourpass
DB_HOST=db
DB_PORT=5432
DEBUG=(bool, False)
SECRET_KEY=(str, 'your django key')
```


На сервере создать и запустить контейнеры Docker:
```
sudo docker-compose up -d
```

После успешной сборки, перейти в контейнер бэка, собрать статику и выполнить миграции:
```
sudo docker exec -it <name_of_backend_continer> bash
python manage.py collectstatic
python manage.py migrate
```

--------
## Автор
Влада Мухатдинова 