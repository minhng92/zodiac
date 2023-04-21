import redis

user_connection = redis.Redis(host='redis_stack', port=6380, decode_responses=True)
a = user_connection.ping()
print("a", a)