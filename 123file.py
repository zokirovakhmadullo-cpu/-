
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3

TOKEN = "SENING_TOKENING"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("stats.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    count INTEGER DEFAULT 0
)
""")
conn.commit()

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    inviter = message.from_user.id
   
    cursor.execute("SELECT count FROM users WHERE user_id=?", (inviter,))
    data = cursor.fetchone()
   
    if data:
        cursor.execute("UPDATE users SET count = count + 1 WHERE user_id=?", (inviter,))
    else:
        cursor.execute("INSERT INTO users (user_id, count) VALUES (?, 1)", (inviter,))
   
    conn.commit()

@dp.message_handler(commands=['top'])
async def top_users(message: types.Message):
    cursor.execute("SELECT user_id, count FROM users ORDER BY count DESC LIMIT 20")
    data = cursor.fetchall()
   
    text = "🏆 Top 20:\n\n"
   
    for i, user in enumerate(data, start=1):
        text += f"{i}. ID: {user[0]} - {user[1]} одам\n"
   
    await message.reply(text)

if __name__ == "__main__":
    executor.start_polling(dp)