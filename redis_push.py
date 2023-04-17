import os
import redis

redis_host = os.getenv("REDIS_HOST", default="redis")
redis_port = int(os.getenv("REDIS_PORT", default="6379"))
redis_db = int(os.getenv("REDIS_DB", default="0"))
redis_pass = str(os.getenv("REDIS_PASS", default=False))

my_key = "minh key"
my_value = "minh's value"

def main():
    client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_pass)        
    try:
        print("---------------------------")
        print("| PUSH KEY VALUE TO REDIS |")
        print("---------------------------")
        client.set(my_key, my_value)
        print("Retrieve pushed key (%s): %s" % (my_key, str(client.get(my_key))))
    except Exception as e:
        print("Error on client connecting to Redis")
        print(e)
    pass
    
if __name__ == "__main__":
    main()
