from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import sqlite3
from datetime import datetime

TOKEN = "SENING_TOKENING"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# DB
conn = sqlite3.connect("stats.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    date TEXT,
    count INTEGER DEFAULT 1
)
""")
conn.commit()

# 📌 MENU
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("🏆 Top 20"),
    KeyboardButton("🎯 Top 10 bugun"),
    KeyboardButton("📊 Mening statim")
)

# 🚀 START
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Менюдан танланг 👇", reply_markup=menu)

# 👥 Yangi user qo‘shildi
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    inviter = message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT count FROM users WHERE user_id=? AND date=?
    """, (inviter, today))
    
    data = cursor.fetchone()
    
    if data:
        cursor.execute("""
        UPDATE users SET count = count + 1 
        WHERE user_id=? AND date=?
        """, (inviter, today))
    else:
        cursor.execute("""
        INSERT INTO users (user_id, date, count) 
        VALUES (?, ?, 1)
        """, (inviter, today))
    
    conn.commit()

# 🏆 TOP 20 (umumiy)
@dp.message_handler(lambda message: message.text == "🏆 Top 20")
async def top_all(message: types.Message):
    cursor.execute("""
    SELECT user_id, SUM(count) as total 
    FROM users 
    GROUP BY user_id 
    ORDER BY total DESC 
    LIMIT 20
    """)
    
    data = cursor.fetchall()
    
    text = "🏆 Umumiy Top 20:\n\n"
    
    for i, user in enumerate(data, start=1):
        text += f"{i}. ID: {user[0]} - {user[1]} одам\n"
    
    await message.answer(text)

# 🎯 TOP 10 BUGUN
@dp.message_handler(lambda message: message.text == "🎯 Top 10 bugun")
async def top_today(message: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
    SELECT user_id, count FROM users 
    WHERE date=? 
    ORDER BY count DESC 
    LIMIT 10
    """, (today,))
    
    data = cursor.fetchall()
    
    if not data:
        await message.answer("Бугун ҳали ҳеч ким одам қўшмаган 😅")
        return
    
    text = "🎯 Bugungi Top 10:\n\n"
    
    for i, user in enumerate(data, start=1):
        text += f"{i}. ID: {user[0]} - {user[1]} одам\n"
    
    await message.answer(text)

# 📊 MY STAT
@dp.message_handler(lambda message: message.text == "📊 Mening statim")
async def my_stat(message: types.Message):
    user_id = message.from_user.id
    
    cursor.execute("""
    SELECT SUM(count) FROM users WHERE user_id=?
    """, (user_id,))
    
    total = cursor.fetchone()[0]
    
    if total:
        await message.answer(f"Сиз жами {total} та одам қўшгансиз 👍")
    else:
        await message.answer("Сиз ҳали ҳеч ким қўшмагансиз 😅")

# ▶️ RUN
if __name__ == "__main__":
    executor.start_polling(dp)
