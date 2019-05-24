from aiocqhttp import CQHttp
import threading
import asyncio

bot = CQHttp(enable_http_post=False)


@bot.on_message()
async def handle_msg(context):
    print(context)
    if context["user_id"] == 498533576:
        await bot.send({"user_id": 498533576}, "Hello!")


def sendmsg():
    asyncio.run(bot.send({"user_id": 498533576}, "Hello! "))


if __name__ == "__main__":
    try:
        bot.run(host="127.0.0.1", port=8090)
    except KeyboardInterrupt:
        print("Exit.")
