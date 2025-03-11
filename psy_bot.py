import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
BOT_TOKEN = "7904391590:AAGeQ-Lcsp5GQEEZLq_4veqsSOITr7xiaE4"
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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
    DAY_3_Q1 = State()
    DAY_3_Q2 = State()
    DAY_4_Q1 = State()
    DAY_5_Q1 = State()
    DAY_6_Q1 = State()
    DAY_7_Q1 = State()
    DAY_7_Q2 = State()
    DAY_8_Q1 = State()
    DAY_9_Q1 = State()
    DAY_10_Q1 = State()
    DAY_11_Q1 = State()
    DAY_12_Q1 = State()
    DAY_13_Q1 = State()
    DAY_14_Q1 = State()

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

    welcome_text = (
        "Привет! 🎉 Добро пожаловать в марафон 'Путь к цели: 14 дней к мечте'!\n"
        "Тебя ждет увлекательное путешествие, где ты определишь свою цель и научишься уверенно к ней двигаться. 🚀\n\n"
        "Начнем прямо сейчас. Напиши, какую цель ты хочешь достичь? (Например: купить машину, выйти на новый доход, сменить работу)"
    )
    await message.answer(welcome_text)
    await MarathonStates.DAY_0_GOAL.set()

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

    await message.answer(
        "Отлично! Давай уточним твою цель по SMART:\n"
        "1️⃣ Конкретная: Что именно ты хочешь достичь?\n"
        "2️⃣ Измеримая: Как ты поймешь, что достиг цели?\n"
        "3️⃣ Достижимая: Реально ли это для тебя?\n"
        "4️⃣ Реалистичная: Есть ли у тебя ресурсы?\n"
        "5️⃣ Ограниченная по времени: Когда ты хочешь это сделать?\n\n"
        "Ответь на эти вопросы, чтобы уточнить цель!"
    )
    await MarathonStates.DAY_0_SMART.set()

@dp.message_handler(state=MarathonStates.DAY_0_SMART)
async def process_day_0_smart(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Отлично! Теперь твоя цель стала четче. Завтра начнем двигаться к ней!\n"
        "💡 Важно четко определить свою цель. Без этого невозможно двигаться вперед."
    )
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
        await message.answer(
            "День 1: Осознание — зачем вам эта цель?\n\n"
            "❓ Упражнение '7 почему?'\n"
            "1️⃣ Напиши, почему ты хочешь достичь этой цели?\n"
            "2️⃣ А теперь спроси себя: почему этот ответ важен?\n"
            "3️⃣ Повтори этот вопрос 7 раз (отвечая каждый раз на свой же ответ).\n\n"
            "Пример:\n"
            "* Я хочу купить машину.\n"
            "* Почему? → Потому что это даст мне свободу.\n"
            "* Почему это важно? → Я смогу больше путешествовать...\n\n"
            "Отправь свои 7 ответов в чат!"
        )
        await MarathonStates.DAY_1_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_1_Q1)
async def process_day_1_q1(message: types.Message, state: FSMContext):
    await message.answer(
        "🔥 Круто! Теперь ты четко понимаешь, зачем тебе эта цель.\n"
        "Напоследок напиши 3 предложения, отвечая на вопрос: 'Зачем мне это?'\n\n"
        "(Пример: 'Я хочу машину, потому что это свобода передвижения. Я смогу путешествовать, работать и жить там, где хочу. Это сделает меня счастливее.')"
    )
    await MarathonStates.DAY_1_Q2.set()

@dp.message_handler(state=MarathonStates.DAY_1_Q2)
async def process_day_1_q2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

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
@dp.message_handler(lambda message: True, state=None)
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

@dp.message_handler(state=MarathonStates.DAY_2_Q1)
async def process_day_2_q1(message: types.Message, state: FSMContext):
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

@dp.message_handler(state=MarathonStates.DAY_2_Q2)
async def process_day_2_q2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Супер! Теперь у тебя настоящая, твоя собственная цель! Ты стал(а) на шаг ближе к ее достижению. 💪\n\n"
        "Завтра мы разберем что мешает тебе двигаться вперед и как убрать преграды! 🚀"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 3 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 3: Разбираем страхи и барьеры
@dp.message_handler(lambda message: True, state=None)
async def day_3_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 3:
        await message.answer(
            "День 3: Разбираем страхи и барьеры\n\n"
            "❓ Ответь на 3 вопроса:\n"
            "1️⃣ Какие 3 причины мешают тебе приблизиться к твоей цели?\n"
            "2️⃣ Какой твой главный страх, связанный с этой целью?\n"
            "3️⃣ Что самое страшное может случиться, если ты попробуешь?\n\n"
            "Напиши свои ответы в чат!"
        )
        await MarathonStates.DAY_3_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_3_Q1)
async def process_day_3_q1(message: types.Message, state: FSMContext):
    await message.answer(
        "🔍 Отлично! Теперь давай глубже разберем твои страхи.\n"
        "Чаще всего они кажутся нам больше, чем есть на самом деле.\n\n"
        "✨ Задание: Используем метод 'А что, если?':\n"
        "1️⃣ Запиши свой страх.\n"
        "2️⃣ Ответь: Что самое страшное случится, если это произойдет?\n"
        "3️⃣ Теперь ответь: Как я справлюсь с этим, если это случится?\n\n"
        "Пример:\n"
        "* Страх: 'Боюсь, что меня не поддержат'.\n"
        "* Самое страшное: 'Я останусь без поддержки, мне будет сложно'.\n"
        "* Как справлюсь: 'Найду других людей, которые меня поддержат, или докажу себе, что могу справиться сам(а)'.\n\n"
        "Напиши свои выводы в чат!"
    )
    await MarathonStates.DAY_3_Q2.set()

@dp.message_handler(state=MarathonStates.DAY_3_Q2)
async def process_day_3_q2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Молодец! Теперь ты видишь, что даже если страх реализуется, ты сможешь с этим справиться! Это делает тебя сильнее. 💪\n\n"
        "Завтра мы переведем твою цель в четкий, структурированный план, чтобы двигаться уверенно! 🚀"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 4 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 4: Где взять ресурс?
@dp.message_handler(lambda message: True, state=None)
async def day_4_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 4:
        await message.answer(
            "День 4: Где взять ресурс?\n\n"
            "❓ Анализ энергозатрат: Что сейчас забирает твою энергию?\n"
            "Напиши, что отнимает у тебя больше всего сил (работа, отношения, привычки и т.д.)?"
        )
        await MarathonStates.DAY_4_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_4_Q1)
async def process_day_4_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Давай высвободим энергию для достижения цели! Подумай, как можно минимизировать этот энергозатратчик.\n"
        "Завтра разберем, как бороться со страхами и прокрастинацией!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 5 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 5: Борьба со страхом и прокрастинацией
@dp.message_handler(lambda message: True, state=None)
async def day_5_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 5:
        await message.answer(
            "День 5: Борьба со страхом и прокрастинацией\n\n"
            "❓ Упражнение: Чего ты боишься, когда думаешь о своей цели?\n"
            "Напиши свои страхи, а потом попробуй ответить: как ты можешь с ними справиться?"
        )
        await MarathonStates.DAY_5_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_5_Q1)
async def process_day_5_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Страх — это нормально. Главное, как ты с ним работаешь!\n"
        "Завтра разберем, как действовать, даже если нет мотивации!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 6 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 6: Как действовать, даже если нет мотивации
@dp.message_handler(lambda message: True, state=None)
async def day_6_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 6:
        await message.answer(
            "День 6: Как действовать, даже если нет мотивации\n\n"
            "❓ Методика '2 минуты': Выбери минимальный шаг к своей цели, который займет не больше 2 минут.\n"
            "Напиши, что это за шаг, и сделай его прямо сейчас!"
        )
        await MarathonStates.DAY_6_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_6_Q1)
async def process_day_6_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Не жди мотивации, создавай её действиями!\n"
        "Завтра проверим твой прогресс и дадим поддержку!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 7 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 7: Проверка прогресса + поддержка
@dp.message_handler(lambda message: True, state=None)
async def day_7_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 7:
        await message.answer(
            "День 7: Проверка прогресса + поддержка\n\n"
            "❓ Что уже получилось на пути к твоей цели? Напиши 3 вещи, которые ты сделал(а) за эту неделю."
        )
        await MarathonStates.DAY_7_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_7_Q1)
async def process_day_7_q1(message: types.Message, state: FSMContext):
    await message.answer(
        "🔥 Класс! Видишь, у тебя уже есть реальные успехи! Теперь сделаем еще одно упражнение.\n"
        "✨ Представь, что ты пишешь письмо самому себе через год. Опиши, каких успехов ты уже добился(ась) и что ты чувствуешь.\n"
        "Пример: 'Привет! Сейчас я смотрю на себя и радуюсь тому, что я достиг своей цели. Я смог(ла) сделать X, у меня есть Y, и я чувствую себя счастливым(ой)!'\n\n"
        "Напиши свое письмо в чат!"
    )
    await MarathonStates.DAY_7_Q2.set()

@dp.message_handler(state=MarathonStates.DAY_7_Q2)
async def process_day_7_q2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Великолепно! Это письмо поможет тебе укрепить веру в себя и свою цель.\n"
        "Завтра мы разберем как закрепить новые привычки и выработать дисциплину!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 8 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 8: Работа с сомнениями
@dp.message_handler(lambda message: True, state=None)
async def day_8_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 8:
        await message.answer(
            "День 8: Работа с сомнениями\n\n"
            "❓ Как ты отвечаешь себе на вопрос 'А вдруг не получится?' Напиши свои мысли."
        )
        await MarathonStates.DAY_8_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_8_Q1)
async def process_day_8_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Преодолей внутреннего критика! Завтра разберем, как окружение влияет на твой успех."
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 9 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 9: Окружение и влияние на результат
@dp.message_handler(lambda message: True, state=None)
async def day_9_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 9:
        await message.answer(
            "День 9: Окружение и влияние на результат\n\n"
            "❓ Как поддержка (или её отсутствие) влияет на тебя? Напиши 3 человека, которые тебя вдохновляют, и 3, кто тормозит."
        )
        await MarathonStates.DAY_9_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_9_Q1)
async def process_day_9_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Ты — это среднее пяти людей, с которыми общаешься. Завтра закрепим результаты!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 10 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 10: Закрепление результатов
@dp.message_handler(lambda message: True, state=None)
async def day_10_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 10:
        await message.answer(
            "День 10: Закрепление результатов\n\n"
            "❓ Напиши, что изменилось за марафон? Какие маленькие победы ты одержал(а)?"
        )
        await MarathonStates.DAY_10_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_10_Q1)
async def process_day_10_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Маленькие победы создают большие изменения! Завтра разберем, как окружение влияет на успех."
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 11 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 11: Как окружение влияет на успех
@dp.message_handler(lambda message: True, state=None)
async def day_11_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 11:
        await message.answer(
            "День 11: Как окружение влияет на успех\n\n"
            "❓ Напиши 3 человека, которые тебя вдохновляют, и 3 человека, которые тормозят твое развитие."
        )
        await MarathonStates.DAY_11_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_11_Q1)
async def process_day_11_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Отлично! Завтра начнем финальные шаги — реальные действия!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 12 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 12: Финальный шаг!
@dp.message_handler(lambda message: True, state=None)
async def day_12_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 12:
        await message.answer(
            "День 12: Финальный шаг!\n\n"
            "❓ Сделай самое важное действие, которое приближает к цели.\n"
            "Напиши в чат: 'Я сделал(а) это!'"
        )
        await MarathonStates.DAY_12_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_12_Q1)
async def process_day_12_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Отлично! Продолжаем движение вперед! Завтра сделаем еще один шаг."
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 13 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 13: Финальный шаг!
@dp.message_handler(lambda message: True, state=None)
async def day_13_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 13:
        await message.answer(
            "День 13: Финальный шаг!\n\n"
            "❓ Сделай еще одно важное действие, которое приближает к цели.\n"
            "Напиши в чат: 'Я сделал(а) это!'"
        )
        await MarathonStates.DAY_13_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_13_Q1)
async def process_day_13_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Великолепно! Завтра подведем итоги марафона!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 14 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# День 14: Итоги и награды
@dp.message_handler(lambda message: True, state=None)
async def day_14_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT marathon_day FROM users WHERE user_id = ?", (user_id,))
    day = c.fetchone()[0]
    conn.close()

    if day == 14:
        await message.answer(
            "День 14: Итоги и награды\n\n"
            "🎉 Поздравляю! Ты прошел(а) марафон и теперь на пути к своей мечте! 🚀\n"
            "🔹 Последнее задание:\n"
            "Напиши, чему ты научился(ась) за 14 дней.\n"
            "Как изменилось твое отношение к цели?\n\n"
            "Напиши свой итог!"
        )
        await MarathonStates.DAY_14_Q1.set()

@dp.message_handler(state=MarathonStates.DAY_14_Q1)
async def process_day_14_q1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(
        "🔥 Ты справился(ась)! Главное – продолжай движение к цели! 💪\n"
        "Спасибо, что прошел(а) марафон со мной!"
    )
    await state.finish()

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET marathon_day = 15 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)