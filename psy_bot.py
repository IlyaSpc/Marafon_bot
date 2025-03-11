import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import requests
import json
import os  # Для переменных окружения
from aiohttp import web  # Для веб-сервера Render

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация планировщика для напоминаний
scheduler = AsyncIOScheduler()
scheduler.start()

# URL для загрузки сообщений из GitHub
MESSAGES_URL = "https://raw.githubusercontent.com/IlyaSpc/Marafon_bot/main/messages.json"

# Загрузка сообщений из облака
def load_messages():
    response = requests.get(MESSAGES_URL)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Не удалось загрузить сообщения из облака")
        return {
            "start": "Ошибка загрузки данных. Напиши свою цель!",
            "day_0_goal": "Ошибка загрузки. Уточни цель по SMART.",
            "day_0_smart": "Ошибка загрузки. Завтра продолжим!",
            "day_1_start": "Ошибка загрузки. Напиши 7 почему."
        }

messages = load_messages()

# Инициализация базы данных SQLite
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        marathon_day INTEGER DEFAULT 0,
        last_message_time TEXT,
        goal TEXT,
        payment_status TEXT DEFAULT 'pending'
    )""")
    conn.commit()
    conn.close()

init_db()

# Определяем состояния для FSM
class MarathonStates(StatesGroup):
    DAY_0_GOAL = State()
    DAY_0_SMART = State()
    DAY_1_Q1 = State()
    DAY_1_Q2 = State()
    DAY_2_Q1 = State()
    DAY_2_Q2 = State()

# Функция для отправки напоминаний
async def send_reminder(user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        logging.error(f"Ошибка при отправке напоминания пользователю {user_id}: {e}")

# Планировщик напоминаний
def schedule_reminders(user_id, state_name):
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=datetime.now() + timedelta(hours=3),
        args=[user_id, "Не откладывай свой успех! Напиши ответ, чтобы продолжить марафон! 💪"],
        id=f"reminder_3h_{user_id}_{state_name}"
    )
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=datetime.now() + timedelta(hours=6),
        args=[user_id, "Разбор твоих ответов поможет двигаться дальше! Напиши их сейчас! 🚀"],
        id=f"reminder_6h_{user_id}_{state_name}"
    )

# Удаление напоминаний после ответа
def remove_reminders(user_id, state_name):
    try:
        scheduler.remove_job(f"reminder_3h_{user_id}_{state_name}")
        scheduler.remove_job(f"reminder_6h_{user_id}_{state_name}")
    except Exception:
        pass

# Стартовая команда /start
@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    # Сохраняем пользователя в базу
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, marathon_day) VALUES (?, ?, ?, ?, ?)",
              (user_id, username, first_name, last_name, 0))
    conn.commit()
    conn.close()

    await message.answer(messages["start"])
    await MarathonStates.DAY_0_GOAL.set()
    schedule_reminders(user_id, "DAY_0_GOAL")

# День 0: Формулировка цели
@dp.message_handler(state=MarathonStates.DAY_0_GOAL)
async def process_day_0_goal(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    goal = message.text

    # Сохраняем цель в базу
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET goal = ? WHERE user_id = ?", (goal, user_id))
    conn.commit()
    conn.close()

    remove_reminders(user_id, "DAY_0_GOAL")

    await message.answer(messages["day_0_goal"])
    await MarathonStates.DAY_0_SMART.set()
    schedule_reminders(user_id, "DAY_0_SMART")

@dp.message_handler(state=MarathonStates.DAY_0_SMART)
async def process_day_0_smart(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    remove_reminders(user_id, "DAY_0_SMART")

    await message.answer(messages["day_0_smart"])
    await state.finish()

    # Обновляем день в базе
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 1: Осознание — зачем вам эта цель?
@dp.message_handler(lambda message: True, state=None)
async def day_1_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 1:
        await message.answer(messages["day_1_start"])
        await MarathonStates.DAY_1_Q1.set()
        schedule_reminders(user_id, "DAY_1_Q1")
    elif day == 2:
        await day_2_start(message)

@dp.message_handler(state=MarathonStates.DAY_1_Q1)
async def process_day_1_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    remove_reminders(user_id, "DAY_1_Q1")

    await message.answer(
        "🔥 Круто! Теперь ты четко понимаешь, зачем тебе эта цель.\n"
        "Напоследок напиши 3 предложения, отвечая на вопрос: 'Зачем мне это?'\n\n"
        "(Пример: 'Я хочу машину, потому что это свобода передвижения. Я смогу путешествовать, работать и жить там, где хочу. Это сделает меня счастливее.')"
    )
    await MarathonStates.DAY_1_Q2.set()
    schedule_reminders(user_id, "DAY_1_Q2")

@dp.message_handler(state=MarathonStates.DAY_1_Q2)
async def process_day_1_q2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    remove_reminders(user_id, "DAY_1_Q2")

    await message.answer(
        "🔥 Ты молодец! Сегодня ты сделал первый шаг. Завтра разберемся, действительно ли эта цель твоя! 🎯\n\n"
        "💡 Совет: подумай сегодня, что мешало тебе раньше двигаться к этой цели. Это поможет нам завтра!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 2 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 2: Проверяем, твоя ли это цель?
async def day_2_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 2:
        await message.answer(
            "День 2: Проверяем, твоя ли это цель?\n\n"
            "❓ Ответь на 3 вопроса:\n"
            "1️⃣ Откуда у тебя появилось это желание? Кто тебя вдохновил на эту цель?\n"
            "2️⃣ Представь, что ты уже достиг(ла) этой цели. Что ты чувствуешь?\n"
            "3️⃣ Если бы никто об этом не знал, ты бы все равно стремился(ась) к этому?\n\n"
            "Напиши свои ответы в чат!"
        )
        await MarathonStates.DAY_2_Q1.set()
        schedule_reminders(user_id, "DAY_2_Q1")

@dp.message_handler(state=MarathonStates.DAY_2_Q1)
async def process_day_2_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    remove_reminders(user_id, "DAY_2_Q1")

    await message.answer(
        "🔍 Отлично! Теперь давай глубже разберем твои истинные желания.\n"
        "Если вдруг ты понял(а), что цель не совсем твоя, давай попробуем скорректировать ее.\n\n"
        "✨ Задание: Подумай, как можно изменить формулировку цели, чтобы она была 100% твоей.\n"
        "Запиши ее в новом варианте!\n\n"
        "Пример:\n"
        "❌ 'Хочу зарабатывать 500 000 в месяц, потому что это круто.'\n"
        "✅ 'Хочу зарабатывать 500 000 в месяц, чтобы путешествовать, чувствовать свободу и выбирать, где жить.'\n\n"
        "Напиши обновленный вариант своей цели!"
    )
    await MarathonStates.DAY_2_Q2.set()
    schedule_reminders(user_id, "DAY_2_Q2")

@dp.message_handler(state=MarathonStates.DAY_2_Q2)
async def process_day_2_q2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    remove_reminders(user_id, "DAY_2_Q2")

    await message.answer(
        "🔥 Супер! Теперь у тебя настоящая, твоя собственная цель! Ты стал(а) на шаг ближе к ее достижению. 💪\n\n"
        "Это пока конец нашего тестового марафона. Напиши, что думаешь о первых днях!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 3 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Веб-сервер для Render
async def health_check(request):
    return web.Response(text="Bot is running")

async def setup_webserver():
    app = web.Application()
    app.add_routes([web.get('/', health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))  # Render использует PORT, по умолчанию 10000
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# Запуск бота и веб-сервера
if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(setup_webserver())
    executor.start_polling(dp, skip_updates=True, loop=loop)