import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylda topilmadi!")

if not OLLAMA_API_KEY:
    raise ValueError("OLLAMA_API_KEY .env faylda topilmadi!")

SYSTEM_PROMPT = """
Sen StudentAI — universal AI yordamchisan.

Foydalanuvchi o'zbekcha yozsa, o'zbekcha javob ber.
Inglizcha yozsa, inglizcha javob ber.
Ruscha yozsa, ruscha javob ber.

Tarjima so'ralsa, tabiiy va professional tarjima qil.
Matematika berilsa, bosqichma-bosqich yech.
Kod berilsa, dasturchi kabi yordam ber.
Ingliz tili bo'yicha tushunarli tushuntir.
Savolga aniq, foydali va tabiiy javob ber.

Bilmagan ma'lumotni uydirma.
"""

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def ask_ollama(user_text: str) -> str:
    url = "https://ollama.com/api/chat"

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-oss:120b",
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
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:

            result = await response.json()

            if response.status != 200:
                error = result.get("error", "Noma'lum API xatosi")
                raise Exception(error)

            return result["message"]["content"]


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "🤖 StudentAI ishga tushdi!\n\n"
        "Savolingizni yuboring."
    )


@dp.message()
async def message_handler(message: types.Message):
    if not message.text:
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )

    try:
        answer = await ask_ollama(message.text)

        # Telegram xabar limiti uchun bo'lib yuborish
        for i in range(0, len(answer), 4000):
            await message.answer(answer[i:i + 4000])

    except Exception as e:
        print("AI ERROR:", e)
        await message.answer(
            "❌ AI bilan bog'lanishda xatolik yuz berdi.\n"
            "CMD oynasidagi xatoni tekshiring."
        )


async def main():
    print("🤖 StudentAI ishga tushmoqda...")
    print("🧠 Ollama Cloud API ulanmoqda...")

    try:
        # API kalitni va modelni tekshirish
        test = await ask_ollama("Salom! Bir so'z bilan salomlash.")
        print("✅ Ollama API ishlayapti.")
        print("🧪 Test:", test[:100])
    except Exception as e:
        print("❌ Ollama API xatosi:", e)
        return

    print("✅ Telegram bot xabar kutmoqda...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
