FROM redis

MAINTAINER Scott Barnes "sgbarnes@protonmail.com"

WORKDIR /

COPY redis.conf /redis.conf
COPY gen-test-certs.sh .

RUN chmod +x gen-test-certs.sh
RUN apt-get -y update && apt-get -y install openssl
RUN sh gen-test-certs.sh
RUN mv tests/tls/redis.crt /
RUN mv tests/tls/redis.key /
RUN mv tests/tls/ca.crt /

EXPOSE 6379
EXPOSE 6380

CMD ["/usr/local/bin/redis-server", "/redis.conf"]