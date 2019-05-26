from itertools import count


class Test:
    counter = count()
    allinstance = []

    def __init__(self):
        self.id = next(self.counter)
        self.allinstance.append(self.id)

    def __contains__(self, other):
        return other in self.allinstance


if __name__ == "__main__":
    t1 = Test()
    t2 = Test()
    print(0 in t1)
