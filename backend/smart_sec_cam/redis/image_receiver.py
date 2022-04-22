import queue
import threading
import time
from typing import List, Dict

import redis


class RedisImageReceiver:
    listener_sleep_time = 0.01

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.message_queue = queue.Queue()
        self.subscribed_channels = []
        self.r_conn = redis.StrictRedis(host=self.redis_host, port=self.redis_port)
        self.pubsub = self.r_conn.pubsub()
        self.listener_thread = None

    def set_channels(self, channels: List[str]):
        self.subscribed_channels = channels
        self._subscribe()

    def add_channel(self, channel: str):
        if channel in self.subscribed_channels:
            raise ValueError("Channel " + str(channel) + " is already in the subscribed channel list")
        self.subscribed_channels.append(channel)
        self._subscribe()

    def remove_channel(self, channel: str):
        self.subscribed_channels.remove(channel)
        self._subscribe()

    def get_all_channels(self) -> List[str]:
        return [key.decode("utf-8") for key in self.r_conn.keys()]

    def has_message(self) -> bool:
        return not self.message_queue.empty()

    def get_message(self) -> Dict[str, any]:
        return self.message_queue.get()

    def start_listener_thread(self):
        listener_thread = threading.Thread(target=self._listen_for_messages)
        listener_thread.start()

    def _subscribe(self):
        self.pubsub.subscribe(*self.subscribed_channels)

    def _redis_message_handler(self, message: any):
        self.message_queue.put(message)

    def _get_new_pubsub_message(self):
        try:
            new_message = self.pubsub.get_message(ignore_subscribe_messages=True)
            if new_message:
                self.message_queue.put(new_message)
        except (redis.exceptions.RedisError, RuntimeError) as e:
            print(e)

    def _listen_for_messages(self):
        while True:
            self._get_new_pubsub_message()
            time.sleep(0.01)
