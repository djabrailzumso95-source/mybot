import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def send_auto_deal():
    try:
        deal_text = (
            "🔥 **Находка дня!**\n\n"
            "Удобный и практичный товар по суперцене. "
            "Отличное качество, высокий рейтинг и быстрая доставка!\n\n"
            "👉 Ссылка на товар: [Посмотреть на Wildberries](https://www.wildberries.ru)"
        )
        await bot.send_message(chat_id=CHANNEL_ID, text=deal_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")

async def background_poster():
    await asyncio.sleep(5)
    while True:
        await send_auto_deal()
        await asyncio.sleep(10800)

async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(web_server())
    asyncio.create_task(background_poster())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
