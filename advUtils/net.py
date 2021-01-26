import inspect
import os
import sys
import traceback
from inspect import isclass
from types import FunctionType, TracebackType, FrameType
from typing import List


def final_attrs(param: List[str]):
    def wrapper(clazz: object):
        if not isclass(clazz):
            raise TypeError("Decorator is not used on class.")

        def replacement(backup):
            # noinspection PyUnusedLocal
            def func_0001(instance: object, name: str, value: object):
                if name in param:
                    raise PermissionError(f"Cannot set final attribute \"{name}\".")
                else:
                    backup(instance, name)
            return func_0001

        if hasattr(clazz, "__setattr__"):
            clazz.__setattr__ = replacement(clazz.__setattr__)

        if hasattr(clazz, "__setattribute__"):
            clazz.__setattribute__ = replacement(clazz.__setattribute__)
        return clazz

    return wrapper


def private_attrs(param: List[str]):
    def wrapper(clazz: object):
        if not isclass(clazz):
            raise TypeError("Decorator is not used on class.")

        def replacement(backup):
            # noinspection PyUnusedLocal
            def func_0001(instance: object, name: str, value: object):

                tb: FrameType = inspect.currentframe()
                print(tb)
                tb = tb.f_back
                print(tb)
                inst = 
                print(inst)
                if name in param:
                    raise PermissionError(f"Cannot set private attribute \"{name}\".")
                else:
                    backup(instance, name)
            return func_0001

        def replacement1(backup):
            # noinspection PyUnusedLocal
            def func_0001(instance: object, name: str):

                tb: FrameType = inspect.currentframe()
                print(tb)
                tb = tb.f_back
                print(tb)

                if name in param:
                    raise PermissionError(f"Cannot get private attribute \"{name}\".")
                else:
                    backup(instance, name)
            return func_0001


        if hasattr(clazz, "__setattr__"):
            clazz.__setattr__ = replacement(clazz.__setattr__)
        if hasattr(clazz, "__getattr__"):
            clazz.__getattr__ = replacement1(clazz.__getattr__)

        if hasattr(clazz, "__setattribute__"):
            clazz.__setattribute__ = replacement(clazz.__setattribute__)
        if hasattr(clazz, "__getattribute__"):
            clazz.__getattribute__ = replacement1(clazz.__getattribute__)
        return clazz

    return wrapper


class Class1:
    def __init__(self):
        self.t1()

    def t1(self):
        self.t2()

    def t2(self):
        self.t3()

    def t3(self):
        self.t4()

    def t4(self):
        self.t5()

    def t5(self):
        tb: FrameType = inspect.currentframe()
        print(tb)
        tb = tb.f_back
        print(tb)


@private_attrs(["value"])
class Socket(object):
    def __init__(self, host: str, port: int):
        self.value = "data"


if __name__ == '__main__':
    Class1()

    Socket("lol", 3)
