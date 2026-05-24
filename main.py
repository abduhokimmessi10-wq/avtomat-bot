import asyncio
import logging
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from google import genai
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8479528381:AAEdHT30__mmNzRpLCpgKnSB2qyfJhW1Iko"
KANAL_USERNAME = "@abdurakhmonov_code"
GEMINI_API_KEY = "AIzaSyC--IclIW4VyU2dgu3OMVAoKbtgRRavgNY"

AUTO_POSTS = [
    {"time": "05:00", "topic": "Muvaffaqiyatli insonlarning tonggi odatlari"},
    {"time": "08:00", "topic": "Xauusd va dollar haqida malumot trading analiz"},
    {"time": "10:00", "topic": "Yaxshi odatlarni rivojlantirish va yomon odatlardan xalos bolish haqida"},
    {"time": "12:00", "topic": "Dasturlashni o'rganishda eng ko'p ketadigan xatolar"},
    {"time": "14:00", "topic": "Islom diniga oid foydali malumotlar"},
    {"time": "15:30", "topic": "Ingliz tilida foydali methodlar va malumotlar"},
    {"time": "17:00", "topic": "Sun'iy intellekt texnologiyalarining kelajagi"},
    {"time": "18:30", "topic": "Biznes va startap boshlash bo'yicha master-klass"},
    {"time": "20:00", "topic": "Vaqtni to'g'ri boshqarish (Time management) usullari"},
    {"time": "21:30", "topic": "Uxlashdan oldin o'qish tavsiya etiladigan kitoblar"}
]
# ====================================================

logging.basicConfig(level=logging.INFO)

app = FastAPI(title='Avtomatik AI Kanal Bot')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Timezone'ni qat'iy belgilaymiz
scheduler = AsyncIOScheduler(timezone='Asia/Tashkent')
client = genai.Client(api_key=GEMINI_API_KEY)


async def generate_useful_content(topic: str) -> str:
    prompt = f"""
    Telegram kanal uchun o'zbek tilida qisqa post yoz.
    Mavzu: "{topic}"

    Qoidalar:
    - Jami 150-200 so'z, ortiq yozma.
    - 1 ta qisqa sarlavha (bold, **)
    - 3-4 asosiy nuqta, har biri 1-2 jumla.
    - 2-3 emoji, ko'p emas.
    - Oxirida 2-3 xeshteg.
    """
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
        )
        return response.text
    except Exception as e:
        return f"⚠️ Xatolik: {str(e)}"


async def send_automatic_post(topic: str):
    print(f"\n🔄 '{topic}' mavzusida post tayyorlanmoqda...")
    post_text = await generate_useful_content(topic)
    try:
        # aiogram v3 uchun parse_mode bot obyektida yoki yuklamada to'g'ri berilishi kerak
        await bot.send_message(
            chat_id=KANAL_USERNAME,
            text=post_text,
            parse_mode="Markdown"
        )
        print("✅ Post kanalga yuborildi!")
    except Exception as e:
        print(f"❌ Yuborishda xatolik: {str(e)}")


@app.on_event("startup")
async def on_startup():
    # Mana shu qatordan boshlab pastdagi barcha qatorlar funksiya ichiga 4 ta probel (yoki 1 ta Tab) bilan surilishi shart!
    asyncio.create_task(dp.start_polling(bot))

    for post in AUTO_POSTS:
        hour, minute = post["time"].split(":")
        scheduler.add_job(
            send_automatic_post,
            'cron',
            hour=int(hour),
            minute=int(minute),
            args=[post["topic"]],
            misfire_grace_time=600
        )

    scheduler.start()
    print("🤖 Bot va taymer muvaffaqiyatli ishga tushdi!")