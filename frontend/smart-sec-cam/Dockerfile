FROM node:14-alpine

WORKDIR /frontend
RUN mkdir -p certs

COPY . .

RUN npm install --silent
RUN npm update
RUN npm audit fix
RUN npx browserslist@latest --update-db
RUN npm install -g serve
RUN npm run build

CMD ["serve", "-s", "build", "-l", "3000", "--ssl-cert", "./certs/sec-cam-server.cert", "--ssl-key", "./certs/sec-cam-server.key"]