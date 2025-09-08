import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import httpx
import re

# === الإعدادات ===
BOT_TOKEN = "8286042975:AAFM9Jp5bn8Cz6_h_iSFdEIMuysoi8B1wbI"
DEEPL_API_KEY = "c0f5583c-3977-4c39-9747-aabf78cd085c:fx"
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
BOT_USERNAME = "@Bo3tbtranslatorbot"

# === التهيئة ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def translate_text(text: str) -> str:
    """ترجمة النص من الإنجليزية إلى العربية باستخدام DeepL"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DEEPL_API_URL,
                headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"},
                data={
                    "text": text,
                    "source_lang": "EN",
                    "target_lang": "AR"
                },
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            return result["translations"][0]["text"]
    except Exception as e:
        logger.error(f"خطأ في الترجمة: {e}")
        return "❌ حدث خطأ أثناء الترجمة."

def is_english_text(text: str) -> bool:
    """التحقق إذا كان النص يحتوي على كلمات إنجليزية (حتى لو مختلط)"""
    if not text or not text.strip():
        return False
    return bool(re.search(r'[a-zA-Z]', text))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل في المجموعات"""
    message = update.message
    chat_id = message.chat_id

    # تجاهل الرسائل الخاصة (البوت يعمل في المجموعات فقط)
    if message.chat.type not in ['group', 'supergroup']:
        return

    text = message.text or ""

    # التحقق إذا تم ذكر البوت
    if BOT_USERNAME in text:
        # التحقق إذا كانت الرسالة تحتوي على ريبلاي
        if not message.reply_to_message:
            await message.reply_text("❌ يجب أن ترد على رسالة تحتوي على نص إنجليزي.")
            return

        # جلب نص الرسالة التي تم الرد عليها
        original_text = message.reply_to_message.text or ""

        # التحقق إذا كان النص إنجليزيًا
        if not is_english_text(original_text):
            await message.reply_text("❌ الرسالة التي رددت عليها لا تحتوي على نص إنجليزي.")
            return

        # ترجمة النص
        translated = await translate_text(original_text)

        # الرد على الرسالة التي تم الرد عليها (الرسالة الأصلية)
        await message.reply_text(
            translated,
            reply_to_message_id=message.reply_to_message.message_id
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأخطاء"""
    logger.error(f"تحديث تسبب في خطأ: {context.error}")

def main():
    """تشغيل البوت"""
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة معالج الرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # إضافة معالج الأخطاء
    application.add_error_handler(error_handler)

    # بدء الاستقبال
    application.run_polling()

if __name__ == "__main__":
    main()
