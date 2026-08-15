import asyncio
import os
import html

import httpx
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =========================================================
# 1. .env faylidan maxfiy ma'lumotlarni olish
# =========================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# Ollama Cloud sozlamalari
OLLAMA_URL = "https://ollama.com/v1/chat/completions"

# Agar Ollama hisobingdagi boshqa modeldan foydalanmoqchi
# bo'lsang, keyinchalik shu nomni o'zgartiramiz.
OLLAMA_MODEL = "gpt-oss:20b"


# =========================================================
# 2. Tokenlarni tekshirish
# =========================================================

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN topilmadi! .env faylini tekshiring."
    )

if not OLLAMA_API_KEY:
    raise ValueError(
        "OLLAMA_API_KEY topilmadi! .env faylini tekshiring."
    )


# =========================================================
# 3. Telegram bot
# =========================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================================================
# 4. Oddiy statistika
# =========================================================

user_messages = {}


def add_message(user_id):
    if user_id not in user_messages:
        user_messages[user_id] = 0

    user_messages[user_id] += 1


# =========================================================
# 5. Asosiy menyu
# =========================================================

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎯 Kun motivatsiyasi"),
            KeyboardButton(text="📚 O'qish")
        ],
        [
            KeyboardButton(text="💬 AI bilan suhbat"),
            KeyboardButton(text="📊 Statistika")
        ],
        [
            KeyboardButton(text="ℹ️ Bot haqida")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Menyudan tanlang..."
)


# =========================================================
# 6. AI uchun asosiy instruktsiya
# =========================================================

SYSTEM_PROMPT = """
Sen StudentAI nomli AI yordamchisan.

Sen talabalar uchun:
- motivatsiya berasan;
- o'qishda yordam berasan;
- o'qish rejasini tuzasan;
- matematika va boshqa fanlarni tushuntirasan;
- vaqtni boshqarish bo'yicha maslahat berasan;
- ingliz tilini o'rganishda yordam berasan;
- talaba bilan samimiy suhbatlashasan.

Uslubing:
- samimiy;
- aqlli;
- tajribali ustozdek;
- oddiy va tushunarli;
- ortiqcha rasmiy emas;
- amaliy.

Javoblarni asosan o'zbek tilida ber.

Agar talaba savol bersa, shunchaki umumiy gap emas,
aniq va foydali javob ber.

Agar kerak bo'lsa:
1. muammoni tushuntir;
2. yechim ber;
3. bajarish uchun kichik qadam ber.

Talabani haqorat qilma yoki ortiqcha bosim qilma.

Javoblarni juda uzun qilma.
"""


# =========================================================
# 7. Ollama AI funksiyasi
# =========================================================

async def ask_ai(user_text):

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "temperature": 0.8,
        "stream": False
    }

    try:

        async with httpx.AsyncClient(timeout=90) as client:

            response = await client.post(
                OLLAMA_URL,
                headers=headers,
                json=data
            )

            response.raise_for_status()

            result = response.json()

            answer = result["choices"][0]["message"]["content"]

            return answer.strip()

    except httpx.TimeoutException:

        return (
            "⏳ AI biroz sekin javob beryapti.\n\n"
            "Iltimos, yana bir marta urinib ko'r."
        )

    except httpx.HTTPStatusError as error:

        print(
            "Ollama HTTP xatosi:",
            error.response.text
        )

        return (
            "⚠️ Ollama AI bilan bog'lanishda muammo yuz berdi.\n\n"
            "API key yoki model sozlamalarini tekshirish kerak."
        )

    except Exception as error:

        print("AI xatosi:", error)

        return (
            "❌ AI bilan bog'lanishda xatolik yuz berdi."
        )


# =========================================================
# 8. /start
# =========================================================

@dp.message(CommandStart())
async def start_handler(message: Message):

    if message.from_user:
        add_message(message.from_user.id)

    name = message.from_user.first_name

    await message.answer(
        f"👋 Salom, <b>{html.escape(name)}</b>!\n\n"
        "Men <b>StudentAI</b> 🤖\n\n"
        "Men senga o'qish, motivatsiya va "
        "rivojlanishda yordam beraman.\n\n"
        "Quyidagi menyudan tanla 👇",
        reply_markup=main_menu,
        parse_mode="HTML"
    )


# =========================================================
# 9. Kun motivatsiyasi
# =========================================================

@dp.message(F.text == "🎯 Kun motivatsiyasi")
async def motivation_handler(message: Message):

    await message.answer(
        "🧠 <b>Motivatsiyang tayyorlanmoqda...</b>",
        parse_mode="HTML"
    )

    prompt = """
Menga bugungi kun uchun kuchli, samimiy va real
motivatsion maslahat ber.

Klişe gaplardan qoch.

Talabaga o'qish va o'z ustida ishlash uchun
ruhiy turtki ber.

Oxirida bugun bajarishi mumkin bo'lgan
bitta kichik vazifani ham ber.

Javob 120-180 so'z atrofida bo'lsin.
"""

    answer = await ask_ai(prompt)

    await message.answer(
        "🎯 <b>Bugungi motivatsiya</b>\n\n"
        + answer,
        parse_mode="HTML"
    )


# =========================================================
# 10. O'qish bo'yicha maslahat
# =========================================================

@dp.message(F.text == "📚 O'qish")
async def study_handler(message: Message):

    await message.answer(
        "📚 <b>O'qish yordamchisi</b>\n\n"
        "Menga yoz:\n\n"
        "• Bugun uchun reja tuzib ber\n"
        "• Diqqatni qanday jamlayman?\n"
        "• Matematikani qanday o'rganaman?\n"
        "• Ingliz tilimni yaxshilash uchun reja ber\n"
        "• Imtihonga qanday tayyorlanaman?\n\n"
        "Men AI orqali yordam beraman. 🤖",
        parse_mode="HTML"
    )


# =========================================================
# 11. AI suhbat rejimi
# =========================================================

@dp.message(F.text == "💬 AI bilan suhbat")
async def ai_chat_button(message: Message):

    await message.answer(
        "💬 <b>AI suhbat rejimi</b>\n\n"
        "Endi menga istalgan savolingni yoz.\n\n"
        "Masalan:\n"
        "👉 Matematikani yaxshi o'rganish uchun nima qilay?\n"
        "👉 Menga 3 soatlik o'qish rejasi tuz.\n"
        "👉 Bugun umuman o'qigim kelmayapti.\n\n"
        "Savolingni yoz 👇",
        parse_mode="HTML"
    )


# =========================================================
# 12. Statistika
# =========================================================

@dp.message(F.text == "📊 Statistika")
async def statistics_handler(message: Message):

    if not message.from_user:
        return

    user_id = message.from_user.id

    count = user_messages.get(user_id, 0)

    await message.answer(
        "📊 <b>Sening statistikang</b>\n\n"
        f"💬 Yuborgan xabarlaring: <b>{count}</b>\n\n"
        "🚀 Keyinchalik bu yerga:\n"
        "🔥 Streak\n"
        "📚 O'qish kunlari\n"
        "🎯 Bajarilgan maqsadlar\n"
        "⏱ O'qish vaqti\n"
        "ham qo'shamiz.",
        parse_mode="HTML"
    )


# =========================================================
# 13. Info
# =========================================================

@dp.message(F.text == "ℹ️ Bot haqida")
async def info_handler(message: Message):

    await message.answer(
        "ℹ️ <b>StudentAI</b>\n\n"
        "🎓 Talabalar uchun AI yordamchi.\n\n"
        "🎯 Motivatsiya\n"
        "📚 O'qish yordamchisi\n"
        "💬 AI suhbat\n"
        "📊 Statistika\n\n"
        "Versiya: <b>1.0</b> 🚀",
        parse_mode="HTML"
    )


# =========================================================
# 14. Boshqa barcha xabarlar → AI
# =========================================================

@dp.message()
async def general_message_handler(message: Message):

    if not message.text:
        return

    # Menyu tugmalarini bu handlerga kiritmaymiz
    menu_buttons = {
        "🎯 Kun motivatsiyasi",
        "📚 O'qish",
        "💬 AI bilan suhbat",
        "📊 Statistika",
        "ℹ️ Bot haqida"
    }

    if message.text in menu_buttons:
        return

    if message.from_user:
        add_message(message.from_user.id)

    # AI yozayotganini ko'rsatamiz
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )

    answer = await ask_ai(message.text)

    await message.answer(answer)


# =========================================================
# 15. Botni ishga tushirish
# =========================================================

async def main():

    print("🤖 StudentAI ishga tushmoqda...")
    print("🧠 Ollama AI ulangan.")
    print("✅ Bot Telegramdan xabar kutmoqda...")

    try:

        await dp.start_polling(bot)

    except Exception as error:

        print("❌ Bot xatosi:", error)

    finally:

        await bot.session.close()


# =========================================================
# 16. START
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())