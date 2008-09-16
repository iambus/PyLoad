
import urllib

proxies = {'http': 'http://localhost:8008'}
print urllib.urlopen('http://kneo:8000/', proxies=proxies).read()

