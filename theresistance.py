import json
import random
from itertools import cycle

from baseplayer import BaseCampaign, BasePlayer
from commandparser import getnumberparser, getboolparser, ErrorString

with open("theresistance.json", encoding="utf8") as f:
    texts = json.load(f)


class TheResistancePlayer(BasePlayer):
    pass


TheResistancePlayer.ROLE.update({"blue": "抵抗组织", "red": "政府卧底"})


class TheResistanceCampaign(BaseCampaign):
    PlayerConfig = {
        5: ["blue"] * 3 + ["red"] * 2,
        6: ["blue"] * 4 + ["red"] * 2,
        7: ["blue"] * 4 + ["red"] * 3,
        8: ["blue"] * 5 + ["red"] * 3,
        9: ["blue"] * 6 + ["red"] * 3,
        10: ["blue"] * 6 + ["red"] * 4,
    }
    MissionRequire = {
        5: (2, 3, 2, 3, 3),
        6: (2, 3, 4, 3, 4),
        7: (2, 3, 3, 4, 4),
        8: (3, 4, 4, 5, 5),
        9: (3, 4, 4, 5, 5),
        10: (3, 4, 4, 5, 5),
    }
    MissionFailOn = {
        5: (1, 1, 1, 1, 1),
        6: (1, 1, 1, 1, 1),
        7: (1, 1, 1, 2, 1),
        8: (1, 1, 1, 2, 1),
        9: (1, 1, 1, 2, 1),
        10: (1, 1, 1, 2, 1),
    }

    def __init__(self, group_id):
        super().__init__(group_id)
        self.missions = ["x"] * 5  # "x"代表未进行，"r"代表卧底成功（任务失败），"b"代表抵抗成功（任务成功）

    def addplayer(self, sender):
        """添加玩家
        Arguments:
            sender {dict} -- 玩家的消息上下文 context["sender"]
        """
        self.players.append(TheResistancePlayer(sender))

    def _start(self):
        """游戏流程"""
        self.assignroles()  # 分发身份
        for p in self.players:  # 告诉玩家自己的身份
            self.addprivatemsg(
                p, texts["ROLE_NOTIFICATION"].format(rolename=p.rolename)
            )
        msg = texts["RED_PLAYER_NOTIFICATION"] + "\n".join(self.redplayername)
        for p in self.redplayers:  # 告诉卧底玩家其它卧底身份
            self.addprivatemsg(p, msg)
        self.addgroupmsg(texts["GAME_START"])
        leadergen = cycle(self.players)
        for _ in range(random.randint(0, self.playernum - 1)):  # 随机初始首领玩家
            next(leadergen)

        gameround = 1  # 执行任务的下标，1-based
        votefailcount = 0  # 选择玩家投票不通过次数，若 ==5 则政府卧底胜利
        missionrequire = self.MissionRequire[self.playernum]  # 任务所需玩家数量
        for leader in leadergen:  # 无限循环，用 break 跳出
            self.addgroupmsg(
                texts["THIS_ROUND_STARTUP"].format(
                    player=leader,
                    gameround=gameround,
                    missionplayernum=missionrequire[gameround - 1],
                )
            )
            self.acceptcommandfrom(
                (leader,),
                getnumberparser(
                    maxnum=self.playernum, commandnumber=missionrequire[gameround - 1]
                ),
            )
            yield self.yieldmessages()
            self.addgroupmsg(
                texts["LEADER_CHOOSE_PLAYER"].format("、".join(self.commands[leader]))
            )
            self.acceptcommandfrom(
                "all", getboolparser(yes=texts["VOTE_AGREE"], no=texts["VOTE_DISAGREE"])
            )
            yield self.yieldmessages()
            # TODO: 游戏流程

    def handlemessage(self, context):
        player = context["user_id"]
        if player not in self.acceptedplayers:
            return None
        cmd = self.commandparsers[player](context["message"])
        if isinstance(cmd, ErrorString):
            return {"reply": texts[cmd]}  # TODO
        else:
            self.commands[player] = cmd
        if all((cmd is not None for cmd in self.commands.values())):  # 收到所有指令
            return self.resume()
        else:
            return None

    @property
    def redplayers(self):
        return (p for p in self.players if p.role == "red")

    @property
    def blueplayers(self):
        return (p for p in self.players if p.role == "blue")

    @property
    def redplayername(self):
        return (p.name for p in self.redplayers)

    @property
    def blueplayername(self):
        return (p.name for p in self.blueplayers)


if __name__ == "__main__":
    missionrequire = TheResistanceCampaign.MissionRequire[6]
    gameround = 1
    print(
        texts["THIS_ROUND_STARTUP"].format(
            player=TheResistancePlayer({"nickname": "六号玩家", "user_id": 498533576}),
            gameround=gameround,
            missionplayernum=missionrequire[gameround - 1],
        )
    )
