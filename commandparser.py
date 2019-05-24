import re


class ErrorString(str):
    pass


def getnumberparser(include=None, exclude=None, commandnumber=1, maxnum=None):
    """返回一个数字解析器。

    Keyword Arguments:
        include {list, tuple, set} -- 允许范围内的数字 (default: {None})
        exclude {list, tuple, set} -- 从允许范围内排除的数字 (default: {None})
        commandnumber {int} -- 需要的指令数量 (default: {1})
        maxnum {int} -- 若 include 不给定，自动设置 include 为 range(1, maxnum + 1) (default: {None})
    """
    if include is None:
        include = set(range(1, maxnum + 1))
    # if exclude is not None:
    #     include -= set(exclude)

    def commandparser(message: str):
        message = message.strip(" ,")
        pattern = (
            r"^[^\d]*"
            + r"[,.\s\u3000\u3001\u3002\uFF0C\uFF1B\u548C]".join(
                [r"(\d+)"] * commandnumber
            )
            + r"[^\d]*$"
        )
        m = re.match(pattern, message)
        try:
            if m is None:
                return ErrorString("INVALID_MESSAGE")
            res = set(map(int, m.groups()))
            if len(res) != commandnumber:
                return ErrorString("DUPLICATED_NUMBERS")
            if any((i not in include for i in res)):
                return ErrorString("INVALID_MESSAGE")
            if any((i in exclude for i in res)):
                return ErrorString("EXCLUDED_NUMBER")
        except ValueError:
            return ErrorString("INVALID_MESSAGE")
        return res

    return commandparser


def getboolparser(yes=None, no=None):
    """返回一个二值（布尔）解析器。

    Keyword Arguments:
        yes {set, tuple, list} -- 真值描述集合 (default: {None})
        no {set, tuple, list} -- 假值描述集合 (default: {None})
    """
    if yes is None:
        yes = {"y"}
    if no is None:
        no = {"n"}

    def commandparser(message):
        msgyes = any((y in message for y in yes))
        msgno = any((n in message for n in no))
        if msgno:
            return False
        elif msgyes:
            return True
        else:
            return ErrorString("INVALID_MESSAGE")

    return commandparser


if __name__ == "__main__":
    commandparser = getnumberparser(exclude=(3,), maxnum=10, commandnumber=3)
    try:
        while True:
            print(commandparser(input()))
    except KeyboardInterrupt:
        pass
