FROM python:3.10-slim-buster

MAINTAINER Scott Barnes "sgbarnes@protonmail.com"

WORKDIR backend/
RUN mkdir -p certs
COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install .[server]