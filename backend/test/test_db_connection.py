import sys

sys.path.append('../backend')
from db_connection import get_connection, get_db
from redis_connection import get_redis_connection

def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"Database connection successful. MySQL version: {version['VERSION()']}")
    finally:
        conn.close()
    r = get_redis_connection()
    try:
        response = r.ping()
        print("Redis connection successful:", response)
    except Exception as e:
        print("Redis connection failed:", e)

if __name__ == "__main__":
    main()