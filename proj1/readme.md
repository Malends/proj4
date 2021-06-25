# Задача

Даны 5 различных функций. Для каждой из функции написать вызов с различными аргументами.

### Функции
```python
def f1(a, b, *args, **kwargs):
    print(a)
    print(b)
    print(args)
    print(kwargs)
    print()

def f2(a, b, *args, c):
    print(a)
    print(b)
    print(args)
    print(c)
    print()

def f3(a, b=None, *args, d=None):
    print(a)
    print(b)
    print(args)
    print(d)
    print()

def f4(a, b, **kwargs):
    print(a)
    print(b)
    print(kwargs)
    print()

def f5(a, b, *, d):
    print(a)
    print(b)
    print(d)
    print()
```
