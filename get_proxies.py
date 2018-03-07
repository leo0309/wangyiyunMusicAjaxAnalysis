import requests
from bs4 import BeautifulSoup
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

