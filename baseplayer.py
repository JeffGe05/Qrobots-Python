import random


class BasePlayer:
    ROLE = {"unassigned": "未分配身份"}

    def __init__(self, sender):
        self.user_id = sender["user_id"]
        self.name = sender.get("card") or sender["nickname"]
        self.role = "unassigned"

    # def __hash__(self):
    #     return hash(self.user_id)

    def assignrole(self, role):
        self.role = role

    @property
    def rolename(self):
        return self.ROLE[self.role]


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

    def assignroles(self):
        """给玩家分配角色"""
        if self.playernum not in self.PlayerConfig:
            print("玩家数量不够或超出。")
            return
        roles = self.PlayerConfig[self.playernum].copy()
        random.shuffle(roles)
        for i, p in enumerate(self.players):
            p.assignrole(roles[i])

    def _start(self):
        yield NotImplemented
        raise NotImplementedError

    def resume(self):
        return next(self._game)

    def addprivatemsg(self, player, msg):
        self.messages.append(({"user_id": player.user_id}, msg))

    def addgroupmsg(self, msg):
        self.messages.append(({"group_id": self.group_id}, msg))

    def yieldmessages(self):
        messages = self.messages
        self.messages = []
        return messages

    def acceptcommandfrom(self, acceptedplayers, commandparsers):
        if isinstance(acceptedplayers, str) and acceptedplayers == "all":
            self.acceptedplayers = self.players
        elif isinstance(acceptedplayers, (set, tuple, list)):
            self.acceptedplayers = acceptedplayers
        else:
            raise NotImplementedError
        self.commands = dict.fromkeys(acceptedplayers, None)
        if isinstance(commandparsers, callable):
            self.commandparsers = dict.fromkeys(acceptedplayers, commandparsers)
        elif isinstance(commandparsers, (tuple, list)):
            self.commandparsers = dict(zip(acceptedplayers, commandparsers))
        else:
            raise NotImplementedError

    def handlemessage(self, context):
        raise NotImplementedError
