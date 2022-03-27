FROM node:16-alpine as build-static

WORKDIR /frontend
RUN mkdir -p certs

COPY frontend/smart-sec-cam/ .

RUN npx browserslist@latest --update-db

RUN npm install
RUN npm update
RUN npm audit fix || true
RUN npm install -g serve
RUN npm run build

FROM python:3.10-slim-buster as run

MAINTAINER Scott Barnes "sgbarnes@protonmail.com"

WORKDIR backend/
RUN mkdir -p certs
COPY backend/ .

COPY --from=build-static /frontend/build/ /backend/build

RUN python -m pip install --upgrade pip
RUN python -m pip install .[server]

ENTRYPOINT /backend/smart_sec_cam/server/docker-entrypoint.sh