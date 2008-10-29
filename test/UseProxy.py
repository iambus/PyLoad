
import urllib

proxies = {'http': 'http://localhost:9008'}
print urllib.urlopen('http://localhost:8000/', proxies=proxies).read()

