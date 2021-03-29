import sys
from multiprocessing.dummy import Pool
global num_lst
num_lst = []


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


def gen(num):
    return num - 1


@tail_call_optimized
def gen2(num):
    num2 = gen(num)
    if num2 < 10:
        num_lst.append(num2)
        return num2
    else:
        p=Pool(2)
        for num in [num - 1, num - 12]:
            num = p.apply_async(gen, (num,))
            num_lst.append(num)
        p.close()
        p.join()
        return gen2(num)


if __name__ == "__main__":
    num = 10234
    gen2(num)
    print(len(num_lst))
