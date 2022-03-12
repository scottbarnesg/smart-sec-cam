# Server is pined to 3.7 because greenthreads break the redis client's SSL conneciton with later versions
FROM python:3.7-slim-buster

MAINTAINER Scott Barnes "sgbarnes@protonmail.com"

WORKDIR backend/
COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install .[server]