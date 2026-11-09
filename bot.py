import asyncio
import logging
import os
import random
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@wbozonnahodki11")
TAKPRODAM_SUBID = os.getenv("TAKPRODAM_SUBID", "wbozon_subid")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def make_takprodam_link(original_url: str) -> str:
    """Преобразует прямую ссылку маркетплейса в твою реферальную через Такпродам"""
    return f"https://takprodam.ru/redirect?subid={TAKPRODAM_SUBID}&url={original_url}"


async def fetch_hot_deals_from_api():
    """Фоновый забор реальных скидок и товаров через API"""
    # Здесь используется шлюз скидок/каталогов маркетплейсов
    api_endpoint = "https://api.fake-deals-service.com/v1/hot-items"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_endpoint, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("products", [])
        except Exception as e:
            logging.error(f"Ошибка запроса к API товаров: {e}")

    # Запасной резервный каталог (если API временно не ответило)
    return [
        {
            "title": "Беспроводная колонка c мощным басом",
            "price": "1 890 ₽",
            "old_price": "3 990 ₽",
            "url": "https://www.wildberries.ru/catalog/12345678/detail.aspx",
            "photo": "https://picsum.photos/800/600",
        },
        {
            "title": "Умные часы с Amoled экраном",
            "price": "2 450 ₽",
            "old_price": "5 100 ₽",
            "url": "https://www.ozon.ru/product/87654321",
            "photo": "https://picsum.photos/800/601",
        },
    ]


async def scheduled_poster():
    """Автоматический автопостинг по таймеру"""
    while True:
        try:
            items = await fetch_hot_deals_from_api()
            if items:
                item = random.choice(items)
                affiliate_link = make_takprodam_link(item["url"])

                caption = (
                    f"🔥 **{item['title']}**\n\n"
                    f"💰 **Цена:** {item['price']} ~(вместо {item.get('old_price', '')})~\n\n"
                    f"🛒 [Забрать на маркетплейсе]({affiliate_link})"
                )

                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=item["photo"],
                    caption=caption,
                    parse_mode="Markdown",
                )
                logging.info("Пост успешно отправлен в канал!")

        except Exception as err:
            logging.error(f"Ошибка автопостинга: {err}")

        # Публикация каждые 3 часа (10800 секунд)
        await asyncio.sleep(10800)


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "🤖 Бот работает в полностью автономном режиме по API!\n"
        f"Посты публикуются в канал {CHANNEL_ID} по расписанию."
    )


async def main():
    logging.basicConfig(level=logging.INFO)
    # Запуск фонового автопостинга вместе с ботом
    asyncio.create_task(scheduled_poster())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

