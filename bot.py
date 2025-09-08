import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === الإعدادات ===
BOT_TOKEN = "8286042975:AAFM9Jp5bn8Cz6_h_iSFdEIMuysoi8B1wbI"
DEEPL_API_KEY = "c0f5583c-3977-4c39-9747-aabf78cd085c:fx"
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
BOT_USERNAME = "@Bo3tbtranslatorbot"

# === إعداد التسجيل (Logging) ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === وظيفة الترجمة عبر DeepL ===
def translate_text(text: str, target_lang: str = "AR", source_lang: str = "EN") -> str:
    try:
        response = requests.post(
            DEEPL_API_URL,
            headers={
                "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "text": text,
                "target_lang": target_lang,
                "source_lang": source_lang
            }
        )
        if response.status_code == 200:
            result = response.json()
            return result["translations"][0]["text"]
        else:
            logger.error(f"DeepL Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception in translate_text: {e}")
        return None

# === معالج الرسائل ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # التحقق: هل الرسالة في مجموعة؟
    if message.chat.type not in ["group", "supergroup"]:
        return

    # التحقق: هل يوجد رد على رسالة؟
    if not message.reply_to_message:
        return

    # التحقق: هل تم منشن البوت في الرسالة الحالية؟
    if BOT_USERNAME not in message.text:
        return

    # جلب نص الرسالة التي تم الرد عليها
    original_text = message.reply_to_message.text
    if not original_text:
        await message.reply_text("❌ لا يمكن الترجمة — الرسالة الأصلية لا تحتوي على نص.")
        return

    # الترجمة
    translated = translate_text(original_text)
    if translated:
        await message.reply_text(f"<translation>:\n{translated}")
    else:
        await message.reply_text("❌ لا يمكن الترجمة — قد لا تكون الرسالة بالإنجليزية أو حدث خطأ.")

# === بدء البوت ===
async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🚀 البوت يعمل...")
    await application.run_polling()

if __name__ == "__main__":
    main()  # بدون asyncio.run()
