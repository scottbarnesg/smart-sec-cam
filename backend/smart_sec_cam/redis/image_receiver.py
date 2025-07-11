from typing import List, Dict

import redis

class RedisImageReceiver:
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.subscribed_channels = []
        self.r_conn = redis.StrictRedis(host=self.redis_host, port=self.redis_port)
        self.pubsub = self.r_conn.pubsub()
        self._subscribe()

    def set_channels(self, channels: List[str]):
        self.subscribed_channels = channels
        self._subscribe()

    def add_channel(self, channel: str):
        if channel in self.subscribed_channels:
            raise ValueError(f"Channel {channel} is already in the subscribed channel list")
        self.subscribed_channels.append(channel)
        self._subscribe()

    def remove_channel(self, channel: str):
        if channel in self.subscribed_channels:
            self.subscribed_channels.remove(channel)
            self._subscribe()

    def get_all_channels(self) -> List[str]:
        return [key.decode("utf-8") for key in self.r_conn.keys()]

    def get_new_message(self):
        try:
            return self.pubsub.get_message(ignore_subscribe_messages=True)
        except (redis.exceptions.RedisError, RuntimeError) as e:
            print(f"Redis error: {e}")
            return None

    def _subscribe(self):
        if self.subscribed_channels:
            self.pubsub.unsubscribe()
            self.pubsub.subscribe(*self.subscribed_channels)