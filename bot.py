from aiocqhttp import CQHttp

from theresistance import TheResistanceCampaign

bot = CQHttp(enable_http_post=False)


@bot.on_message()
async def handle_msg(context):
    pass
    # print(context)
    # if context["user_id"] == 498533576:
    #     await bot.send({"user_id": 498533576}, "Hello!")


def test_setup():
    from time import sleep

    campaign = TheResistanceCampaign(719231968)
    campaign.addplayer({"nickname": "一号玩家", "user_id": 498533576})
    campaign.addplayer({"nickname": "二号玩家", "user_id": 498533576})
    campaign.addplayer({"nickname": "三号玩家", "user_id": 498533576})
    campaign.addplayer({"nickname": "四号玩家", "user_id": 498533576})
    campaign.addplayer({"nickname": "五号玩家", "user_id": 498533576})
    campaign.addplayer({"nickname": "六号玩家", "user_id": 498533576})
    sendmessages(campaign.resume())

    sleep(5)


def sendmessages(messages):
    import threading

    print(messages)
    for context, message in messages:
        threading.Thread(target=sendmessage, args=(context, message)).start()


def sendmessage(context, message):
    import asyncio

    print()
    print(context)
    print(message)
    asyncio.run(bot.send(context, message))


if __name__ == "__main__":
    import threading

    try:
        threading.Timer(5, test_setup).start()
        bot.run(host="127.0.0.1", port=8090)
    except KeyboardInterrupt:
        print("Exit.")
