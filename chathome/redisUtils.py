import redis


class RedisUtils:
    def __init__(self, host='176.10.10.230', port=6401, db=3):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db, decode_responses=True)

    def __enter__(self):
        self.conn = redis.Redis(connection_pool=self.pool)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def hasKey(self, key):
        self.conn.ping()
        if self.conn.exists(key):
            if self.conn.llen(key) > 0:
                return True
        return False

    def getNext(self, key):
        self.conn.ping()
        return self.conn.lpop(key)

    def pushKey(self, key, value):
        self.conn.ping()
        self.conn.rpush(key, value)

    def getHashKeys(self, name):
        self.conn.ping()
        if self.conn.exists(name):
            return self.conn.hkeys(name)

    def getHashByKeyAnd(self, name, key):
        self.conn.ping()
        if self.conn.exists(name):
            value = self.conn.hget(name, key)
            return value
        
    # 删除hash中的某个key
    def delHashByKey(self, name, key):
        self.conn.ping()
        if self.conn.exists(name):
            self.conn.hdel(name, key)
