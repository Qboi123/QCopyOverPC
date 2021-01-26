class Class1(object):
    def __init__(self):
        pass


class Class2(Class1):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    instance = Class2()

    print(isinstance(instance, Class1))
