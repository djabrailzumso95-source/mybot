import asyncio
import logging
import os
import random
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@wbozonnahodki11")
TAKPRODAM_API_KEY = os.getenv("TAKPRODAM_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def fetch_takprodam_products():
    """Запрос реальных товаров через официальный API Такпродам"""
    url = "https://app.takprodam.ru/api/v1/products"  # Официальный эндпоинт API
    headers = {
        "Authorization": f"Bearer {TAKPRODAM_API_KEY}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                url, headers=headers, params={"limit": 20}, timeout=15
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Возвращаем список товаров из ответа
                    return data.get("results", data.get("items", []))
                else:
                    logging.error(f"Ошибка API Такпродам: Статус {resp.status}")
        except Exception as e:
            logging.error(f"Ошибка подключения к API Такпродам: {e}")

    return []


async def scheduled_poster():
    """Фоновый автопостинг по расписанию"""
    while True:
        try:
            products = await fetch_takprodam_products()

            if products:
                item = random.choice(products)

                title = item.get("name", item.get("title", "Отличный товар"))
                price = item.get("price", "Уточняйте по ссылке")
                old_price = item.get("old_price", "")
                
                # Приоритет отдаем партнерской ссылке
                link = item.get("affiliate_link") or item.get("url") or item.get("link", "")
                photo = item.get("image") or item.get("photo") or "https://via.placeholder.com/600"

                # Проверяем корректность ссылки, если она относительная
                if link and not link.startswith("http"):
                    link = f"https://takprodam.ru{link}"

                price_str = f"💰 <b>Цена:</b> {price}"
                if old_price:
                    price_str += f" <s>(вместо {old_price})</s>"

                # Форматирование через HTML, чтобы ссылки не ломались
                caption = (
                    f"🔥 <b>{title}</b>\n\n"
                    f"{price_str}\n\n"
                    f'🛒 <a href="{link}">Забрать на маркетплейсе</a>'
                )

                if link:
                    await bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=photo,
                        caption=caption,
                        parse_mode="HTML",
                    )
                    logging.info("Пост из API Такпродам успешно выложен в канал!")
                else:
                    logging.warning("У выбранного товара отсутствует ссылка.")
            else:
                logging.warning(
                    "Список товаров пуст или API не вернуло данные. Пробуем позже."
                )

        except Exception as err:
            logging.error(f"Ошибка при автопостинге: {err}")

        # Публикация каждые 3 часа (10800 секунд)
        await asyncio.sleep(10800)


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "🤖 Бот успешно подключен к API Такпродам!\n"
        f"Автопостинг работает в канале {CHANNEL_ID}."
    )


async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(scheduled_poster())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
