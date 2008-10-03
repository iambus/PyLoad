
import urllib

proxies = {'http': 'http://localhost:8008'}
print urllib.urlopen('http://localhost:8000/', 'hehe', proxies=proxies).read()

