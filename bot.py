import asyncio
from defaultdict import DefaultDict

from aiocqhttp import CQHttp

from theresistance import TheResistanceCampaign

bot = CQHttp(enable_http_post=False)
group_message_handler = DefaultDict(default_group_message_handler)
private_message_handler = DefaultDict(default_private_message_handler)
campaigns = dict()


def default_group_message_handler(context):
    at_me = f"[CQ:at,qq={context['self_id']}]"
    message = context["message"]
    group_id = context["group_id"]
    user_id = context["user_id"]

    # 忽略没有at机器人的消息
    if at_me not in message:
        return

    # 忽略已经在其他群进行游戏的QQ号消息，防止无法确定私聊消息应该交给哪个游戏处理
    if user_id in private_message_handler:
        return {"reply": "你已经在其它群的游戏中了……"}  # TODO:文字移到外部json文件中

    # 预先防止群内已有游戏进行，但此代码应该不会被执行，因为后续群消息应该都交给其它message_handler处理了
    if group_id in group_message_handler:
        print("This line of code should not be excecuted. Please check.")
        return

    # 抵抗组织
    if "抵抗组织" in message:  # TODO:文字移到外部json文件中
        campaign = TheResistanceCampaign(group_id)
        campaigns[group_id] = campaign
        campaign.addplayer(context["sender"])
        name = campaign.players[0].name
        group_message_handler[group_id] = campaign.handlemessage
        private_message_handler[user_id] = campaign.handlemessage
        return {"reply": f"{name}发起了抵抗组织游戏，发送“加入游戏”来参与吧！"}  # TODO:文字移到外部json文件中


def default_private_message_handler(context):
    pass


@bot.on_message()
async def handle_msg(context):
    print(context)  # Debug

    # TODO: 添加游戏结束后移除message_handler的代码

    if context["message_type"] == "private":
        ret = private_message_handler[context["user_id"]](context)
    elif context["message_type"] == "group":
        ret = group_message_handler[context["group_id"]](context)
    else:
        print("Unknown message type. Please check.")
        return

    if isinstance(ret, dict) and "reply" in ret:
        return ret
    elif ret is None:
        return
    elif isinstance(ret, list):
        await sendmessages(ret)


async def sendmessages(messages):
    coros = []
    for context, message in messages:
        # Debug: 去除QQ号后面添加的id
        # if "user_id" in context:
        #     context["user_id"] = context["user_id"] // 10

        coros.append(bot.send(context, message))

    await asyncio.gather(*coros)


if __name__ == "__main__":
    try:
        bot.run(host="127.0.0.1", port=8090)
    except KeyboardInterrupt:
        print("Exit.")
