import json
import random
from itertools import cycle
from collections import Counter

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

    def addplayer(self, sender):
        """添加玩家
        Arguments:
            sender {dict} -- 玩家的消息上下文 context["sender"]
        """
        self.players.append(TheResistancePlayer(sender))

    def _start(self):
        """游戏流程"""
        # 游戏准备
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
        missionfailon = self.MissionFailOn[self.playernum]  # 任务失败所需的不配合票数
        missions = ["x"] * 5  # "x"代表未进行，"r"代表卧底成功（任务失败），"b"代表抵抗成功（任务成功）

        # 游戏开始
        for leader in leadergen:  # 无限循环，用 break 跳出
            # 讨论，首领选择执行任务玩家
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

            # 所有玩家投票是否通过首领选择出任务的玩家
            missionplayersid = self.commands[leader.user_id]
            self.addgroupmsg(
                TEXT["VOTE_LEADER_CHOOSE_PLAYER"].format(
                    missionplayers=self.playerstringat(missionplayersid),
                    votecount=votefailcount + 1,
                )
            )
            self.addprivatemsgforall(TEXT["VOTE_BEGIN"])
            self.acceptcommandfrom(
                "all", getboolparser(yes=TEXT["VOTE_AGREE"], no=TEXT["VOTE_DISAGREE"])
            )
            yield self.yieldmessages()

            # 投票不通过，更换首领，继续
            voteyescount = sum(self.commands.values())  # 通过的玩家数
            if voteyescount <= self.playernum / 2:  # 如果一半及以上的玩家否决了本回合首领任命的人选
                self.addgroupmsg(TEXT["VOTE_NOT_PASSED"])
                votefailcount += 1
                if votefailcount == 5:
                    winners = "red"
                    break
                continue

            # 投票通过，开始执行任务
            self.addgroupmsg(TEXT["VOTE_PASSED"])
            votefailcount = 0
            missionplayers = tuple(map(self.getplayerbyid, missionplayersid))
            for p in missionplayers:
                self.addprivatemsg(
                    p,
                    TEXT["MISSION_VOTE_" + str(missionfailon[gameround - 1])].format(
                        gameround=gameround
                    ),
                )
            self.acceptcommandfrom(
                missionplayers,
                getboolparser(yes=TEXT["MISSION_COOP"], no=TEXT["MISSION_NOT_COOP"]),
            )
            yield self.yieldmessages()

            # 判断任务是否成功完成
            missionnotcoopcount = sum((not cmd for cmd in self.commands.values()))
            if missionnotcoopcount < missionfailon[gameround - 1]:
                missions[gameround - 1] = "b"
                if missionnotcoopcount == 1:
                    self.addgroupmsg(TEXT["MISSION_SUCCESS_WITH_1_NOTCOOP"])
                else:
                    self.addgroupmsg(TEXT["MISSION_SUCCESS"])
            else:
                missions[gameround - 1] = "r"
                self.addgroupmsg(
                    TEXT["MISSION_FAIL"].format(notcoop=missionnotcoopcount)
                )

            # 判断胜利条件
            missioncount = Counter(missions)
            if "r" in missioncount and missioncount["r"] >= 3:
                winners = "red"
                break
            elif "b" in missioncount and missioncount["b"] >= 3:
                winners = "blue"
                break

            # 继续下一项任务
            gameround += 1

        # end for leader in leadergen

        # 宣布胜利阵营
        self.addgroupmsg(
            TEXT["GAME_END"].format(winners=TheResistancePlayer.ROLE[winners])
        )
        self.gameended = True
        yield self.yieldmessages()

    def handlemessage(self, context):

        # TODO: 判断私聊还是群聊，作出不同响应；添加玩家加入响应代码；添加游戏开始代码

        user_id = context["user_id"]
        message = context["message"]

        # Debug: 消息中'#'前面是添加的id
        # message = message.split("#")
        # if len(message) > 1:
        #     user_id = user_id * 10 + int(message[0])
        #     message = message[1]
        # else:
        #     message = message[0]

        # 忽略非接收指令玩家和已设定指令玩家的所有消息
        if user_id not in self.acceptedplayers or self.commands[user_id] is not None:
            return None

        cmd = self.commandparsers[user_id](message)
        if isinstance(cmd, ErrorString):
            return {"reply": TEXT[cmd]}
        else:
            self.commands[user_id] = cmd

        if self.allplayerset:  # 收到所有指令
            self.addprivatemsg(user_id, TEXT["COMMAND_RECEIVED"])
            return self.resume()
        else:
            return {"reply": TEXT["COMMAND_RECEIVED"]}

    @property
    def redplayers(self):
        return tuple(p for p in self.players if p.role == "red")

    @property
    def blueplayers(self):
        return tuple(p for p in self.players if p.role == "blue")

    @property
    def redplayername(self):
        return tuple(p.name for p in self.redplayers)

    @property
    def blueplayername(self):
        return tuple(p.name for p in self.blueplayers)


if __name__ == "__main__":
    pass
