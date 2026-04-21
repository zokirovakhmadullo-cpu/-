import os
import logging
from datetime import datetime
import sqlite3
from contextlib import contextmanager

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Configuration
TOKEN = os.getenv("BOT_TOKEN", "SENING_TOKENING")  # Use env var
DB_FILE = "stats.db"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Logging setup
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Bot initialization
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Database context manager
@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database schema"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, date)
        )
        """)
        conn.commit()
        logger.info("Database initialized")

# Menu
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("🏆 Top 20"),
    KeyboardButton("🎯 Top 10 bugun"),
    KeyboardButton("📊 Mening statim")
)

# Handlers
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Start command handler"""
    try:
        await message.answer("Менюдан танланг 👇", reply_markup=menu)
    except Exception as e:
        logger.error(f"Start handler error: {e}")

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    """Track new members"""
    try:
        # Get the new member(s)
        for new_user in message.new_chat_members:
            user_id = new_user.id
            today = datetime.now().strftime("%Y-%m-%d")
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (user_id, date, count) VALUES (?, ?, 1)
                ON CONFLICT(user_id, date) DO UPDATE SET count = count + 1
                """, (user_id, today))
                conn.commit()
                logger.info(f"User {user_id} added on {today}")
    except Exception as e:
        logger.error(f"New member handler error: {e}")

@dp.message_handler(lambda message: message.text == "🏆 Top 20")
async def top_all(message: types.Message):
    """Global top 20 handler"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT user_id, SUM(count) as total 
            FROM users 
            GROUP BY user_id 
            ORDER BY total DESC 
            LIMIT 20
            """)
            data = cursor.fetchall()
        
        if not data:
            await message.answer("Ҳали ҳеч ким қўшилмаган 😅")
            return
        
        text = "🏆 Umumiy Top 20:\n\n"
        for i, (user_id, count) in enumerate(data, start=1):
            text += f"{i}. ID: {user_id} - {count} одам\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Top all handler error: {e}")
        await message.answer("Хатолик юз берди 😕")

@dp.message_handler(lambda message: message.text == "🎯 Top 10 bugun")
async def top_today(message: types.Message):
    """Today's top 10 handler"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        with get_db() as conn:
            cursor = conn.cursor()
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
        for i, (user_id, count) in enumerate(data, start=1):
            text += f"{i}. ID: {user_id} - {count} одам\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Top today handler error: {e}")
        await message.answer("Хатолик юз берди 😕")

@dp.message_handler(lambda message: message.text == "📊 Mening statim")
async def my_stat(message: types.Message):
    """User statistics handler"""
    try:
        user_id = message.from_user.id
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT SUM(count) FROM users WHERE user_id=?
            """, (user_id,))
            result = cursor.fetchone()
        
        total = result[0] if result[0] else 0
        
        if total:
            await message.answer(f"Сиз жами {total} та одам қўшгансиз 👍")
        else:
            await message.answer("Сиз ҳали ҳеч ким қўшмагансиз 😅")
    except Exception as e:
        logger.error(f"My stat handler error: {e}")
        await message.answer("Хатолик юз берди 😕")

# Main
if __name__ == "__main__":
    init_db()
    logger.info("Bot started")
    executor.start_polling(dp)
