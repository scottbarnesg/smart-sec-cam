FROM python:3.8-buster

MAINTAINER Scott Barnes "scott.barnes.g@gmail.com"

WORKDIR /backend
COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

CMD ["python", "server.py", "--redis-url", "redis"]