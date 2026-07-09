import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_last_news = {}

def get_last_news():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, title, url FROM articles ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        rows = [(f"Ошибка БД: {e}", "")]

    conn.close()
    return rows

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Обновить новости")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f'Привет, {message.from_user.full_name}! 🤖\n'
        'Я бот игровых новостей iXBT. Скоро я научусь отдавать тебе статьи из базы данных!',
        reply_markup=main_keyboard
    )

@dp.message(lambda message: message.text == "🔄 Обновить новости" or message.text == "/news")
async def cmd_news(message: types.Message):
    news_list = get_last_news()

    if not news_list:
        await message.answer('В базе данных пока нет новостей. Сначала запусти парсер!')
        return
    
    latest_db_id = news_list[0][0]
    user_id = message.from_user.id

    if user_id in user_last_news and user_last_news[user_id] == latest_db_id:
        await message.answer('В БД нет новых новостей! Ты уже видел все самое свежее на момент парсинга.')
        return
    
    user_last_news[user_id] = latest_db_id

    response = "📰 **Последние новости:**\n\n"
    for news_id, title, url in news_list:
        if url:
            response += f"🔹 [{title}]({url})\n\n"
        else:
            response += f"🔹 {title}\n\n"

    await message.answer(response, parse_mode='Markdown', disable_web_page_preview=True)

async def main():
    print('Бот запущен и готов к работе...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())