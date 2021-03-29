import sys


class TailRecurseException(BaseException):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


def tail_call_optimized(g):
    def func(*args, **kwargs):
        f = sys._getframe()
        # sys._getframe(0).f_code.co_name  当前函数名

        if f.f_back and f.f_back.f_back and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        else:
            while 1:
                try:
                    return g(*args, **kwargs)
                except TailRecurseException as e:

                    args = e.args
                    kwargs = e.kwargs

    func.__doc__ = g.__doc__
    return func


if __name__ == "__main__":
    @tail_call_optimized
    def gen2(num):
        num -= 1
        if num <= 10:
            return 10
        else:
            return gen2(num)


    num = 100234
    print(gen2(num))
