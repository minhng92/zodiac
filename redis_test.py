import os
import redis

redis_host = os.getenv("REDIS_HOST", default="redis")
redis_port = int(os.getenv("REDIS_PORT", default="6379"))
redis_db = int(os.getenv("REDIS_DB", default="0"))
redis_pass = str(os.getenv("REDIS_PASS", default="repycon@#2022"))

def main():
    client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_pass)        
    try:
        print("------------------------")
        print("| REDIS KEY VALUE SHOW |")
        print("------------------------")
        for idx, key in enumerate(client.scan_iter()):
            print("%d. %s @ %s" % (idx+1, key, str(client.get(key))))
    except:
        print("Error on client connecting to Redis")
    pass

    print(client.get("abc"))
    
if __name__ == "__main__":
    main()
