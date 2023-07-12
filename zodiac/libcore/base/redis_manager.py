import redis
from .app_singleton import AppSingleton
from .conf_manager import conf_manager

class RedisManager(AppSingleton):
    def __init__(self):
        base_conf = conf_manager[conf_manager.base]
        self.conn = redis.from_url(base_conf["redis_url"])
        print("Initialized Redis connection from url:", base_conf["redis_url"])
        pass
        
    def get_conn(self):
        return self.conn

redis_manager = RedisManager()
