
from time import clock

def fib1(n):
	return 1 if n <= 2 else fib1(n-1) + fib1(n-2)

def fib2(n):
	a, b = 1, 1
	while n > 2:
		a, b = b, a+b
		n -= 1
	return b

x1 = clock()
fib1(30)
x2 = clock()
print int(1000*(x2 - x1))

x1 = clock()
fib2(50000)
x2 = clock()
print int(1000*(x2 - x1))

