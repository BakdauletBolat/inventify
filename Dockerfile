# pull official base image
FROM python:3.11-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1


ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add -u make postgresql-dev gcc python3-dev musl-dev  zlib-dev jpeg-dev build-base libffi-dev


# poetry.lock обязателен: без него poetry резолвит зависимости заново по
# диапазонам из pyproject.toml, и образ получает версии новее зафиксированных
# (так в прод уехал drf-api-logger 1.4.0 вместо 1.1.16 из лока).
COPY pyproject.toml poetry.lock ./

# install dependencies
RUN pip install --upgrade pip
# Версия poetry закреплена: формат lock-файла привязан к мажорной версии,
# а `pip install poetry` ставит последнюю и может отказаться читать лок.
RUN pip install "poetry==1.8.3"
RUN poetry install --no-root

# copy project
COPY . .