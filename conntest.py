import asyncio
import telegram

pp = telegram.request._httpxrequest.HTTPXRequest(proxy='socks5://127.0.0.1:1089')

async def main():
    bot = telegram.Bot("7156890309:AAFOhkmgYUK4uo23NsK_KsCTrl-eSjZahFw", 
                       request=pp)
    async with bot:
        print(await bot.get_me())


if __name__ == '__main__':
    asyncio.run(main())