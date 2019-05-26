from itertools import count


class Test:
    counter = count()

    def __init__(self):
        self.id = next(self.counter)

    def __repr__(self):
        return f"Test({self.id})"

    def __hash__(self):
        return hash(self.id)


if __name__ == "__main__":
    t1 = Test()
    t2 = Test()
    di = {t1: "t1", t2: "t2"}
    print(t1)
    print(t2)
    print(di)
    print(di[t1])
    print(t1 in di)
    print(0 in di)
