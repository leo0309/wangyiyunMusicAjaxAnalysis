import redis
import mmh3
import math

#bloomFilter implemented by redis
class redisBloomFilter:
    #for hash seed(prime number)
    seeds =(101,103,107,109,113,127,131,137,139,149)

    def __init__(self,capacity,error_rate,name, host='localhost', port=6379,db=0):    
        self.__pool = redis.ConnectionPool(host=host,port=port,db=db)
        self.__r = redis.Redis(connection_pool=self.__pool)
        self.capacity = capacity
        self.name = name
        self.__hash_count = math.ceil(-1.43*math.log(error_rate))
        print(self.__hash_count)
        #the size of bit
        self.__bit_count = math.ceil(1.43*self.__hash_count*self.capacity)
        print(self.__bit_count)
    
    def add(self,value):
        value_hash = (mmh3.hash(value,i) % self.__bit_count for i in redisBloomFilter.seeds)
        try:
            pipe = self.__r.pipeline()
            for offset in value_hash:
                pipe.setbit(self.name,offset,1)
            pipe.execute()

        except redis.exceptions.ExecAbortError as e:
            print(e)

    def __contains__(self,value):
        value_hash = (mmh3.hash(value,i) % self.__bit_count for i in redisBloomFilter.seeds)
        for offset in value_hash:
            if not self.__r.getbit(self.name,offset):
                return False
        return True


