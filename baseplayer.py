import random


class BasePlayer:
    ROLE = {"unassigned": "未分配身份"}

    def __init__(self, sender):
        self.user_id = sender["user_id"]
        self.name = sender.get("card") or sender["nickname"]
        self.role = "unassigned"
        self.player_id = None

    # def __hash__(self):
    #     return hash(self.user_id)

    def assignrole(self, role):
        self.role = role

    @property
    def rolename(self):
        return self.ROLE[self.role]

    @property
    def string(self):
        return f"[{self.player_id}] {self.name}"

    @classmethod
    def updaterolenames(cls, roles: dict):
        cls.ROLE.update(roles)


class BaseCampaign:
    PlayerConfig = dict()

    def __init__(self, group_id):
        self.group_id = group_id
        self.players = []
        self._game = self._start()
        self.messages = []
        self.acceptedplayers = ()
        self.commands = dict()
        self.commandparsers = dict()

    def addplayer(self, sender):
        raise NotImplementedError

    @property
    def playernum(self):
        """返回玩家数量"""
        return len(self.players)

    @property
    def allplayerset(self):
        """返回是否已收到所有玩家的指令"""
        return all((cmd is not None for cmd in self.commands.values()))

    def assignroles(self):
        """给玩家分配角色，并打乱座次"""
        if self.playernum not in self.PlayerConfig:
            print("玩家数量不够或超出。")  # TODO
            return
        roles = self.PlayerConfig[self.playernum].copy()
        player_ids = list(range(1, self.playernum + 1))
        random.shuffle(roles)
        random.shuffle(player_ids)
        for i, p in enumerate(self.players):
            p.assignrole(roles[i])
            p.player_id = player_ids[i]
        self.players.sort(key=lambda p: p.player_id)

    def _start(self):
        yield NotImplemented
        raise NotImplementedError

    def resume(self):
        try:
            return next(self._game)
        except StopIteration:
            print("游戏结束")  # TODO
            return None

    def addprivatemsg(self, player, msg):
        self.messages.append(({"user_id": player.user_id}, msg))

    def addprivatemsgforall(self, msg):
        for p in self.players:
            self.addprivatemsg(p, msg)

    def addgroupmsg(self, msg):
        self.messages.append(({"group_id": self.group_id}, msg))

    def yieldmessages(self):
        messages = self.messages
        self.messages = []
        return messages

    def acceptcommandfrom(self, acceptedplayers, commandparsers):
        """设置允许接收指令的玩家。

        Arguments:
            acceptedplayers {str, iterable[Player]} -- 允许发送指令的玩家，'all'代表所有玩家
            commandparsers {callable, iterable[callable]} -- 设置玩家指令的解析器，单个代表解析器设置给所有玩家
        """
        if isinstance(acceptedplayers, str) and acceptedplayers == "all":  # 所有玩家
            acceptedplayers = self.players
        elif isinstance(acceptedplayers, (set, tuple, list)):  # 部分玩家
            # acceptedplayers = acceptedplayers
            pass
        else:
            raise NotImplementedError

        self.acceptedplayers = (p.user_id for p in acceptedplayers)  # 转换为QQ号(int)
        acceptedplayers = None  # Debug: 防止下面代码误用

        self.commands = dict.fromkeys(self.acceptedplayers, None)  # 清空指令缓存

        if callable(commandparsers):  # 单个解析器分配给所有acceptedplayers
            self.commandparsers = dict.fromkeys(self.acceptedplayers, commandparsers)
        elif isinstance(commandparsers, (tuple, list)):  # 解析器列表按顺序分配给acceptedplayers
            if len(self.acceptedplayers) != len(commandparsers):  # 长度不匹配，抛出ValueError异常
                raise ValueError
            if isinstance(self.acceptedplayers, set):  # 集合无顺序，抛出ValueError异常
                raise ValueError
            self.commandparsers = dict(zip(self.acceptedplayers, commandparsers))
        else:
            raise NotImplementedError

    def handlemessage(self, context):
        raise NotImplementedError

    @property
    def allplayerstring(self):
        return "\n".join((p.string for p in self.players))

    def getplayerbyid(self, id):
        for p in self.players:
            if p.player_id == id:
                return p

    def playerstringat(self, player_ids):
        if isinstance(player_ids, int):
            return self.getplayerbyid(player_ids).string

        player_ids = list(player_ids).sort()
        return "\n".join((self.getplayerbyid(player_id) for player_id in player_ids))
