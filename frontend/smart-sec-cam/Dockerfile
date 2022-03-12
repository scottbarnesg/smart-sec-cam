FROM node:14-alpine

MAINTAINER Scott Barnes "scott.barnes.g@gmail.com"

WORKDIR /frontend

COPY . .

RUN npm install --silent
RUN npm update
RUN npm audit fix
RUN npx browserslist@latest --update-db
RUN npm install -g serve
RUN npm run build

CMD ["serve", "-s", "build", "-l", "8443", "--ssl-cert", "./certs/fullchain.pem", "--ssl-key", "./certs/privkey.pem"]