import numpy
from oscopy import Signal

a = Signal('v1', 'V')
a.data = numpy.arange(10, dtype='float')

b = Signal('v2', 'V')
b.data = numpy.arange(10, 20)

# arithmetics
print a
print b
print a + b
print a - b

a += b
print a
a -= b
print a

print a * b
a *= b
print a

a /= b
print a
print b / a

a -= 100 * b
print a
print -a
a += b * 100
print a + b * b - 12

# iteration
print tuple(a)

