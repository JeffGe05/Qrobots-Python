import json
import random
from itertools import cycle

from baseplayer import BaseCampaign, BasePlayer
from commandparser import getnumberparser, getboolparser, ErrorString

with open("theresistance.json", encoding="utf8") as f:
    TEXT = json.load(f)


class TheResistancePlayer(BasePlayer):
    pass


TheResistancePlayer.updaterolenames(TEXT["ROLENAMES"])


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
            self.addprivatemsg(p, TEXT["ROLE_NOTIFICATION"].format(rolename=p.rolename))

        msg = TEXT["RED_PLAYER_NOTIFICATION"] + "\n".join(self.redplayername)
        for p in self.redplayers:  # 告诉卧底玩家其它卧底身份
            self.addprivatemsg(p, msg)
        self.addgroupmsg(TEXT["GAME_START"])
        leadergen = cycle(self.players)
        for _ in range(random.randint(0, self.playernum - 1)):  # 随机初始首领玩家
            next(leadergen)

        gameround = 1  # 执行任务的下标，1-based
        votefailcount = 0  # 选择玩家投票不通过次数，若 ==5 则政府卧底胜利
        missionrequire = self.MissionRequire[self.playernum]  # 任务所需玩家数量
        for leader in leadergen:  # 无限循环，用 break 跳出
            self.addgroupmsg(
                TEXT["THIS_ROUND_STARTUP"].format(
                    player=leader,
                    gameround=gameround,
                    missionplayernum=missionrequire[gameround - 1],
                )
            )
            self.addprivatemsg(
                leader, TEXT["LEADER_CHOOSE_PLAYER"].format(self.allplayerstring)
            )
            self.acceptcommandfrom(
                (leader,),
                getnumberparser(
                    maxnum=self.playernum, commandnumber=missionrequire[gameround - 1]
                ),
            )
            yield self.yieldmessages()

            self.addgroupmsg(
                TEXT["VOTE_LEADER_CHOOSE_PLAYER"].format(
                    self.getplayerbyid(self.commands[leader])
                )
            )
            self.addprivatemsgforall(TEXT["VOTE_BEGIN"])
            self.acceptcommandfrom(
                "all", getboolparser(yes=TEXT["VOTE_AGREE"], no=TEXT["VOTE_DISAGREE"])
            )
            yield self.yieldmessages()

            voteyescount = sum(self.commands.values())  # 通过的玩家数
            if voteyescount <= self.playernum / 2:  # 如果一半及以上的玩家否决了本回合首领任命的人选
                self.addgroupmsg(TEXT["VOTE_NOT_PASSED"])
                continue

            self.addgroupmsg(TEXT["VOTE_PASSED"])

            # TODO: 游戏流程

    def handlemessage(self, context):
        player = context["user_id"]
        if player not in self.acceptedplayers:
            return None

        cmd = self.commandparsers[player](context["message"])
        if isinstance(cmd, ErrorString):
            return {"reply": TEXT[cmd]}
        else:
            self.commands[player] = cmd

        # TODO: 回复指令已收到

        if self.allplayerset:  # 收到所有指令
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
    pass
