
import sys
sys.path.append('../../src')


raw_request = '''POST / HTTP/1.1
accept-language: en-us
accept-encoding: gzip, deflate
connection: close
accept: image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, application/x-ms-application, application/x-ms-xbap, application/vnd.ms-xpsdocument, application/xaml+xml, */*
user-agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; InfoPath.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)
host: www.google.com
cookie: 1234567890ABCDEF
ua-cpu: x86

something
'''

def run():
	from Requester import Requester
	for i in range(10000):
		Requester('http://www.hello.com', raw_request)

import profile
#run()
profile.run('run()', 'x.prof')




