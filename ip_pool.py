import time

import redis
import requests
from bs4 import BeautifulSoup


class IpPool(object):
    def __init__(self, redis):
        self.redis = redis
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
        }

    def get_item(self, url, encoding_format):
        response = requests.get(url, headers=self.headers)
        response.encoding = encoding_format
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".table tr")
        for item in items:
            item = item.text
            yield item.strip().split('\n')

    def get_proxy(self, proxies, number, total, type_number, host, port):
        proxies = proxies
        for i in range(number):
            for i in range(total):
                if proxies:
                    proxy = dict()
                    proxy_mid = proxies.__next__()
                    if len(proxy_mid[type_number]) != 2:
                        proxy[proxy_mid[type_number]] = proxy_mid[host] + '//' + proxy_mid[port]
                        if self.test(proxy):
                            self.write(str(proxy))
                        else:
                            print('验证失败' + ':' + proxy)
                else:
                    break
            time.sleep(3)

    def kuaidaili(self):
        url_list = ['https://www.kuaidaili.com/free', 'https://www.kuaidaili.com/free/inha/2']
        for url in url_list:
            proxies = self.get_item(url, 'utf-8')
            return proxies
            time.sleep(2)

    def get_kuaidaili(self):
        proxies = self.kuaidaili()
        print(proxies)
        try:
            self.get_proxy(proxies, 2, 16, 3, 0, 1)
        except:
            pass

    def ip3366(self):
        url = 'http://www.ip3366.net/?stype=1&page=1'
        proxies = self.get_item(url, 'gb2312')
        return proxies

    def get_ip3366(self):
        proxies = self.ip3366()
        try:
            self.get_proxy(proxies, 1, 10, 3, 0, 1)
        except:
            pass

    def test(self, proxies):
        url = 'http://www.baidu.com'
        try:
            response = requests.get(url, headers=self.headers, proxies=proxies, timeout=10)
        except:
            pass
        else:
            if response.status_code == 200:
                return True

    def write(self, proxy):
        if self.redis.scard('proxy') < 25:
            self.redis.sadd('proxy', proxy)

    def redis_del(self, proxy):
        if type(proxy) is not str:
            proxy = str(proxy)
        try:
            redis.srem('proxy', proxy)
        except:
            pass

    def get(self):
        proxy = redis.sscan_iter('proxy')
        return proxy.__next__()


def main():
    redis_con = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)
    while True:
        ip = IpPool(redis_con)
        ip.get_kuaidaili()
        ip.get_ip3366()
        time.sleep(600)


if __name__ == '__main__':
    main()
