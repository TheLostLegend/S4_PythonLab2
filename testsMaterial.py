import math


def func_with_import_func(x):
    return math.sin(x)


t1 = [[2, 3], [2, ["dw", "xxa"], ["xas"]]]

t2 = {"asda": [3, 4], "wer": 5}

t3 = [{"sdf": [4]}, 6]

objects = [{}, []]

string = "4 43    43"


def simple_func():
    some_field = "asd"
    pass


gl1 = 53


def func_with_globals_and_builtins():
    func = simple_func
    return gl1


def func_in_func(a, f, l):
    a = a + 1

    def first(b):
        b = b + a

    first(f)


def func_with_defaults(a=1, b=3):
    return a + b


def func_with_args_sum(*args):
    res = 0
    for i in args:
        res += i
    return res


def func_with_args_d(**args):
    return args


def p(a=simple_func):
    return a


simplelambda = lambda x: x * x


lambda_in_lambda = lambda x: simplelambda(x) * x


def lambda_in_function(a=2):
    return simplelambda(a)


class Empty_cls:
    pass


class Simple_cls:
    a = 666
    b = [333, 666, 'www']


class Cls_with_inheritance(Empty_cls):
    a = 666
    b = [333, 666, 'www']


class Cls_with_staticmethod:
    @staticmethod
    def hello():
        return 'hello'


class Cls_with_classmethod:
    @classmethod
    def cls(cls):
        return cls


class Inherited_cls(Simple_cls, Cls_with_staticmethod):
    pass
