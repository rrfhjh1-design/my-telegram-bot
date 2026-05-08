import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# --- بياناتك التي أرسلتها تم وضعها هنا بدقة ---
API_TOKEN = '6744737551:AAG33T8ZIjOihTrVHW_2gPBCZf7xcZY3bI0'
ADMIN_ID = 1254750804
CHANNEL_ID = -1002037943578  # تم إضافة -100 ليعمل كآيدي قناة رسمي
# ------------------------------------------

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()
database = {}

# 1. التقاط المنشورات من القناة وحفظها تلقائياً
@dp.channel_post()
async def auto_index(message: types.Message):
    if message.chat.id == CHANNEL_ID:
        # نأخذ النص سواء كان نصاً عادياً أو وصفاً لصورة (Caption) مع التنسيقات
        text = message.html_text if message.text else message.caption
        if text:
            # نستخدم أول سطر من المنشور كعنوان للبحث عنه لاحقاً
            key = text.split('\n')[0][:50]
            database[key] = {"text": text, "id": message.message_id}
            print(f"✅ تمت أرشفة منشور جديد: {key}")

# 2. أمر البحث للمستخدمين
@dp.message(F.text.startswith("ابحث"))
async def search(message: types.Message):
    query = message.text.replace("ابحث", "").strip()
    # البحث عن الكلمة داخل العناوين المؤرشفة
    results = [v for k, v in database.items() if query.lower() in k.lower()]
    
    if results:
        for res in results:
            # إنشاء رابط المنشور في القناة
            url = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{res['id']}"
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🔗 فتح الرابط", url=url)],
                [types.InlineKeyboardButton(text="↩️ رجوع", callback_data="back")]
            ])
            # إرسال المنشور للمستخدم كما هو (عريض، مشوش، إلخ) مع زر الرابط
            await message.answer(res['text'], reply_markup=kb)
    else:
        await message.answer(f"❌ لم أجد نتائج لـ '{query}'.. تأكد من كتابة الاسم كما هو في القناة.")

# 3. أمر بسيط للتأكد من أن البوت يعمل
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 أهلاً بك! البوت جاهز للبحث.\n\nفقط اكتب: **ابحث اسم المسلسل**")

async def main():
    print("🚀 البوت بدأ العمل الآن...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Exit")
