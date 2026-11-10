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

# Ключевые слова для фильтрации нужных категорий
TARGET_KEYWORDS = [
    # Электроника и гаджеты
    "часы",
    "наушники",
    "смарт",
    "телефон",
    "зарядка",
    "кабель",
    "колонка",
    "павербанк",
    "лампа",
    "гаджет",
    "планшет",
    "электро",
    "триммер",
    "робот",
    # Одежда и аксессуары
    "платье",
    "костюм",
    "куртка",
    "рубашка",
    "футболка",
    "джинсы",
    "обувь",
    "кроссовки",
    "штаны",
    "худи",
    "свитшот",
    "пальто",
    "сумка",
    "рюкзак",
    "очки",
    # Товары для дома
    "посуда",
    "нож",
    "органайзер",
    "коврик",
    "плед",
    "подушка",
    "постельное",
    "набор",
    "дозатор",
    "сушилка",
    "скатерть",
    "стакан",
    "кружка",
    "держатель",
    "полка",
    "находка",
]


async def fetch_takprodam_products():
    """Запрос товаров через официальный API Такпродам"""
    url = "https://app.takprodam.ru/api/v1/products"
    headers = {
        "Authorization": f"Bearer {TAKPRODAM_API_KEY}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        try:
            # Запрашиваем побольше товаров (например, 50), чтобы было из чего выбрать подходящие
            async with session.get(
                url, headers=headers, params={"limit": 50}, timeout=15
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("results", data.get("items", []))
                else:
                    logging.error(f"Ошибка API Такпродам: Статус {resp.status}")
        except Exception as e:
            logging.error(f"Ошибка подключения к API Такпродам: {e}")

    return []


def filter_products(products):
    """Фильтрация товаров по нужным категориям"""
    filtered = []
    for item in products:
        title = item.get("name", item.get("title", "")).lower()
        # Проверяем, есть ли хоть одно ключевое слово в названии товара
        if any(keyword in title for keyword in TARGET_KEYWORDS):
            filtered.append(item)
    return filtered


async def scheduled_poster():
    """Фоновый автопостинг по расписанию с фильтрацией"""
    while True:
        try:
            products = await fetch_takprodam_products()

            if products:
                # Фильтруем только электронику, одежду и дом
                filtered_products = filter_products(products)

                # Если по фильтру ничего не нашлось, берем общий список, чтобы бот не молчал
                pool = filtered_products if filtered_products else products
                item = random.choice(pool)

                title = item.get("name", item.get("title", "Отличный товар"))
                price = item.get("price", "Уточняйте по ссылке")
                old_price = item.get("old_price", "")

                # Приоритет партнерской ссылке
                link = (
                    item.get("affiliate_link")
                    or item.get("url")
                    or item.get("link", "")
                )
                photo = (
                    item.get("image")
                    or item.get("photo")
                    or "https://via.placeholder.com/600"
                )

                if link and not link.startswith("http"):
                    link = f"https://takprodam.ru{link}"

                price_str = f"💰 <b>Цена:</b> {price}"
                if old_price:
                    price_str += f" <s>(вместо {old_price})</s>"

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
                    logging.info("Отфильтрованный товар успешно опубликован!")
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
        "🤖 Бот успешно настроен на категории: Электроника, Одежда, Дом!\n"
        f"Автопостинг работает в канале {CHANNEL_ID}."
    )


async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(scheduled_poster())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
