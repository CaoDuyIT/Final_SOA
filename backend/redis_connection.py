import redis

def get_redis_connection():
    return redis.StrictRedis(
    host='127.0.0.1',
    port=6379,
    db=0,
    decode_responses=True  # chuyển byte → string tự động
)