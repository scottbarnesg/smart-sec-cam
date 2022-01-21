FROM python:3.10-slim-buster

MAINTAINER Scott Barnes "scott.barnes.g@gmail.com"

WORKDIR backend/
COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install .[detector]