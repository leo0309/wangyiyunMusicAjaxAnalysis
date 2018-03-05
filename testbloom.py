import gevent
from gevent import monkey
monkey.patch_all()
import requests
from bs4 import BeautifulSoup
import re
import random
import sys
from bloom import bloomFilter
#获取代理
def get_proxies():
    proxies_url = "http://www.xicidaili.com/"
    proxies_headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'zip, deflate',
        'Connection':'keep-alive',
        'Host':'www.xicidaili.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    }
    proxies = []
    #发出请求
    r = requests.get(proxies_url,headers=proxies_headers)
    #解析html
    soup = BeautifulSoup(r.text,'lxml')
    ip_table = soup.find(id='ip_list')
    rows = ip_table.find_all('tr')
    for r in rows:
        if r.img:
            t_d = r.find_all('td')
            proctol = t_d[5].string.lower()
            if proctol in ('http','https'):
                _url = '{}://{}:{}'.format(proctol,t_d[1].string,t_d[2].string)
                proxies.append((proctol,_url))
    return tuple(proxies)

proxies = None
def testBloom(capacity,error_rate,url_seed,headers):
    """
    capacity:数据量
    error_rate:错误率
    proxies:代理
    """
    url_set = set()
    bloom_filter = bloomFilter(capacity,error_rate)
    BFS(url_seed,headers,proxies,url_set,bloom_filter)
    count = 0
    for s in url_set:
        if not s in bloom_filter:
            count +=1
    actual_error_rate = count/len(url_set)
    size = sys.getsizeof(bloom_filter)
    result = {'capacity':capacity,'error_rate_expected':error_rate,
            'actual_error_rate':actual_error_rate,'bloom_size(b)':size}
    print(result)

def BFS(url,headers,proxies,url_set,bloom_filter):
    if len(url_set) >= bloom_filter.capacity:
        return
    try:
        r = requests.get(url,headers=headers,timeout=10)
        print(r)
    except TimeoutError as e:
        print(e)
        BFS(url,headers,proxies,url_set,bloom_filter)
    soup = BeautifulSoup(r.text,'lxml')
    links = soup.find_all("a")
    
    for link in links:
        if len(url_set) >= bloom_filter.capacity:
            return
        if  ('href=\"http' in str(link)):
            href = link['href']
            url_set.add(href)
            bloom_filter.add(href)
    
    if len(url_set)< bloom_filter.capacity:
        temp_set = set(url_set)
        for link in temp_set:
            gevent.sleep(10)
            BFS(link,headers,proxies,url_set,bloom_filter)

#for test
if __name__ == '__main__':
    url_seed = "http://www.ifeng.com/"
    headers = {
        'Host':'www.ifeng.com',
        'Connection':'keep-alive',
        'Pragma':'no-cache',
        'Cache-Control':'no-cache',
        'Upgrade-Insecure-Requests':"1",
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'en-US,en;q=0.9',
        'Cookie':'prov=cn025; city=0514; weather_city=js_yz; region_ip=117.91.73.x; region_ver=1.2; areamainIndexAdd=NaN; ifengRotator_Ap40=0; userid=1520058647464_tkb49r3695; ifengRotator_Ap4132=4; ifengRotator_iis3=7; ifengRotator_AP2567=2; ifengRotator_Ap33=3; ifengRotator_ArpAdPro_2950=0',    
    }
    """
    result = testBloom(1000,0.1,url_seed,headers)
    print(result)
    """   
    capacityTuple = (10,100,1000)
    error_rate = 0.38
    result = []
    for capacity in capacityTuple:
        result.append(gevent.spawn(testBloom,capacity,error_rate,url_seed,headers))
    gevent.joinall(result)