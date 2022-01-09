from typing import Union

import redis


class RedisImageSender:
    def __init__(self, redis_channel: str, redis_host: str = "localhost", redis_port: int = 6380):
        self.redis_channel = redis_channel
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.r_conn = redis.StrictRedis(host=self.redis_host, port=self.redis_port, ssl=True, ssl_cert_reqs=None)
        self.pubsub = self.r_conn.pubsub()

    def send_message(self, message: Union[str, bytes]):
        self.r_conn.set(self.redis_channel, message)
        self.r_conn.publish(self.redis_channel, message)
