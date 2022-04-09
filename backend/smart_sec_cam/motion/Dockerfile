FROM python:3.10-slim-buster

MAINTAINER Scott Barnes "sgbarnes@protonmail.com"

WORKDIR backend/
COPY . .

# Install FFMPEG
RUN apt update && apt -y upgrade && apt install -y ffmpeg

# Install python package
RUN python -m pip install --upgrade pip
RUN python -m pip install .[detector]