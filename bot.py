import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
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
    await asyncio.sleep(5) # Пауза перед первым постом
    while True:
        await send_auto_deal()
        # Интервал между постами: 3 часа (10800 секунд)
        await asyncio.sleep(10800)

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Запуск фонового постинга в канал
    asyncio.create_task(background_poster())
    
    # Настройка веб-сервера для Render (чтобы хостинг видел активность)
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    # Запуск поллинга бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

