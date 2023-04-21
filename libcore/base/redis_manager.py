import redis
from .singleton_class import SingletonClass

from tornado.options import options

class RedisManager(SingletonClass):
    def __init__(self):
        self.conn = redis.from_url(options.redis_url)
        print("Ping redis", self.conn.ping(), options.redis_url)
        print(self.conn.set('foo', 'bar'))
        pass
        
    def get_conn(self):
        return self.conn
