import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Bu yerda botga qanday yordamchi bo'lishi kerakligini uqtiramiz
SYSTEM_PROMPT = """
Sen Abdulazizov Mansurbek tomonidan yaratilgan aqlli Sun'iy Intellekt yordamchisan. 
Foydalanuvchining har qanday savoliga aniq, foydali va professional tarzda javob berasan. 
Matnlarni tarjima qilish, har qanday tilga tarjima qilish albatta foydalanuvchui senday qaysi tilga tarjima qilish kerakligi aytadi,savollarga javob berish va g'oyalar topishda yordam berasiz.
"""

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Salom! Men  Sun'iy Intellekt yordamchisiman. Menga istalgan savol bering yoki matn yuboring, yordam berishga tayyorman! 🤖")

@dp.message(F.text)
async def text_handler(message: Message):
    # Foydalanuvchi yuborgan xabarni to'g'ridan-to'g'ri Gemini modeliga yuboramiz
    chat = model.start_chat(history=[])
    response = chat.send_message(f"{SYSTEM_PROMPT}\n\nFoydalanuvchi: {message.text}")
    await message.answer(response.text)

@dp.message(F.photo)
async def photo_handler(message: Message):
    await message.answer("🔍 Rasmni o'qib chiqayapman...")
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file_info.file_path)
    
    image_data = {
        "mime_type": "image/jpeg",
        "data": photo_bytes.read()
    }
    
    response = model.generate_content([SYSTEM_PROMPT, "Bu rasmda nima tasvirlangan yoki undagi matnni tushuntirib ber:", image_data])
    await message.answer(response.text)

async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
