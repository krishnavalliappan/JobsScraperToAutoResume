import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

class ProxyRotator:
    def __init__(self):
        self.proxies = None
        self.current_proxy = None

    def get_proxy(self):
        if self.proxies:
            self.current_proxy = random.choice(self.proxies)
            return {'all': self.current_proxy, 'https': self.current_proxy, 'http': self.current_proxy}
        else:
            self.proxies = self.get_working_proxies()
            self.current_proxy = random.choice(self.proxies)
            return {'all': self.current_proxy, 'https': self.current_proxy}

    def remove_current_proxy(self):
        if self.current_proxy in self.proxies:
            self.proxies.remove(self.current_proxy)

    @staticmethod
    def get_proxies():
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        proxies = []
        table = soup.find('table', class_='table table-striped table-bordered')
        if table:
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    tds = row.find_all('td')
                    ip = tds[0].text.strip()
                    port = tds[1].text.strip()
                    proxies.append(f'http://{ip}:{port}')
            else:
                print("No table body found")
        else:
            print("No table found")
        return proxies

    @staticmethod
    def check_proxy(proxy):
        try:
            response = requests.get('https://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=5)
            if response.status_code == 200:
                return proxy
        except:
            pass
        return None

    def get_working_proxies(self):
        proxies = self.get_proxies()
        working_proxies = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_proxy = {executor.submit(self.check_proxy, proxy): proxy for proxy in proxies}
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result:
                    working_proxies.append(result)
                    
        print(f"proxy count: {len(working_proxies)}")
        
        return working_proxies

    def refresh_proxies(self):
        self.proxies = self.get_working_proxies()


# if __name__ == "__main__":
#     proxy_rotator = ProxyRotator()
    
#     print("Initial working proxies:")
#     for proxy in proxy_rotator.proxies:
#         print(proxy)
    
#     print("\nGetting a proxy:")
#     proxy = proxy_rotator.get_proxy()
#     print(proxy)
    
#     print("\nRemoving current proxy:")
#     proxy_rotator.remove_current_proxy()
#     print(f"Proxies left: {len(proxy_rotator.proxies)}")
    
#     print("\nRefreshing proxies:")
#     proxy_rotator.refresh_proxies()
#     print(f"New proxy count: {len(proxy_rotator.proxies)}")
