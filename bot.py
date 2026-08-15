import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import google.generativeai as genai

# Tokenlarni olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini AI sozlamalari
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Bot tizim ko'rsatmasi (System Prompt)
SYSTEM_PROMPT = """
Sen Abdulazizov Mansurbek tomonidan yaratilgan professional tarjimon AI botisan.

Sening yagona vazifang:
1. Foydalanuvchi yuborgan har qanday matnni yoki rasmdagi matnni tahlil qilib, uni avtomatik aniqlab, mos ravishda tarjima qilib berish.
2. Agar matn o'zbek tilida bo'lsa -> rus va ingliz tillariga tarjima qil.
3. Agar matn boshqa tilda bo'lsa -> o'zbek tiliga tarjima qil.
4. Ortiqcha suhbatlashma, keraksiz savollar berma va faqat aniq, to'g'ri tarjimani taqdim et.
5. Seni kim yaratganini so'rashsa: "Meni Abdulazizov Mansurbek yaratgan" deb javob ber.
"""

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Salom! Men universal tarjimon botman. 🌐\n\n"
        "Menga har qanday tildagi **matn** yoki **rasm** yuboring, "
        "men uni darhol tarjima qilib beraman!"
    )

# Matnli xabarlarni tarjima qilish
@dp.message(F.text)
async def text_translate_handler(message: Message):
    prompt = f"{SYSTEM_PROMPT}\n\nFoydalanuvchi matni: {message.text}"
    response = model.generate_content(prompt)
    await message.answer(response.text)

# Rasmlardagi matnlarni tahlil qilish va tarjima qilish
@dp.message(F.photo)
async def photo_translate_handler(message: Message):
    await message.answer("🔍 Rasm tahlil qilinmoqda va tarjima qilinmoqda...")
    
    # Rasmni yuklab olish
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file_info.file_path)
    
    image_data = {
        "mime_type": "image/jpeg",
        "data": photo_bytes.read()
    }
    
    # Gemini Vision orqali tahlil qilish
    response = model.generate_content([SYSTEM_PROMPT, image_data])
    await message.answer(response.text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
