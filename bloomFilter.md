### bloomFilter

在一个待处理的资源集中如何判定里面是否有重复元素。最简单的就是查看每一个元素的hash值（可以采用md5之类的算法）。如果hash值相同，则可以有很大程度确定元素重复。但是当数据量十分巨大的时候，直接存储hash值集合，将会增大内存。这时可以利用bit位的思想。生成一个_m_位的bit数组。直接利用最基本的hash算法来计算元素的hash值。将计算出来的hash值散列到bit数组中（hash%_m_），将m位bit数组中命中的位置1。由于bit数组的大小是有限的，如果只使用一个hash函数，会造成碰撞的发生。所以为了解决碰撞问题，可以加入_k_个不同的hash函数，来进行上述计算过程。

判定过程如下：

任取一元素，计算_k_次hash，在_m_中查找是否有相应的bit被置1，如果没有，结束过程，可以判定该元素和已加入元素不同。如果没有找到，则有可能该元素已加入之中。

该思想即是bloomFilter的基本原理。

但是_m_，_k_该如何进行选取呢？

BloomFilter有一个很关键的指标，错误率error_rate（某元素实际上不在，但未识别出来）。

假设数据量有_N_个。

error_rate=识别错误个数/数据量_N_.

由于数据量很大，由大数定律，该error_rate逼近其概率。

做一次hash，某一位置置1的概率为$$1/m$$,没有置1的概率为：$$1-1/m$$。

总共做了_k_次hash（独立过程），某一位置仍没有置1的概率，$$（1-1/m）^k$$。

总共有_N_个数，要做N次上述过程，则某一位置仍没有置1的概率为$$(1-1/m)^{Nk}$$，置1的概率为$$1-（1-1/m）^{Nk}$$。

检测过程错误概率为：$$error\_rate=（1-（1-1/m）^{Nk}）^k$$.

为了使上述值最小，取多大的_k_合适？

利用重要极限:

$$error\_rate=(1-e^{(-Nk/m)})^k$$

求使得_error_rate_最小的k值：

令$$p_0=e^{(-Nk/m)}$$，反解出_k_,得到$$k=-m/N*lnp_0$$，从而有：

$$ln(error\_rate)=-m/N*ln(1-p_0)*lnp_0$$，

由对称性，可知$$p_0=1-p_0$$时，即$$p_0=1/2$$时，

可知$$ln(error\_rate)$$最小。

此时可以得到：

$$k=m/N*ln2$$

代入上述_k_,可以得到此时_m_为：

$$m=-N*ln(error\_rate)/(ln2)^2$$

在最优_k_的表达式中，替换掉_m_，可得：

$$k=-ln(error\_rate)/ln(2)$$

我们可以利用python来模拟该过程，利用python的bitarray，以及第三方库mmh3(用来计算hash)。

```python
from bitarray import bitarray
import math
import mmh3
class bloomFilter:

    def __init__(self, capacity, error_rate):
        """
        capactiy:(int) the size of inputs
        error_rate:(float) the error rate can be accepted
        """
        #the best hash_count speculated
        self.capacity = capacity
        self.__hash_count = math.ceil(-1.43*math.log(error_rate))
        #the size of bitarrary
        self.__bit_count = math.ceil(1.43*self.hash_count*self.capacity)
        self.__bit_array = bitarray(self.bit_count)
        self.__bit_array.setall(0)

    def __len__(self):
        return len(self.__bit_array)

    def add(self,value):
        for i in range(self.__hash_count):
            h = mmh3.hash(str(value),i+17)%self.__bit_count
            self.__bit_array[h] = 1

    def __contains__(self,value):
        for i in range(self.__hash_count):
            h = mmh3.hash(str(value),17+i)%self.__bit_count
            if self.__bit_array[h] == 0:
                return False
        return True

    def __iter__(self):
        return iter(self.__bit_array)

    @property
    def hash_count(self):
        return self.__hash_count
    
    @property
    def bit_count(self):
        return self.__bit_count

    @property
    def bit_array(self):
        return self.__bit_array
```



由于实际开发过程中，一般用redis来实现，redis有一个bitmap数据结构，可以利用setbit,getbit来实现。

```python
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
```

最后以requests结合gevent爬取凤凰网首页，获得所有\<a\> 连接的href，进行宽度优先遍历，对上述方法进行测试。

源码详见



