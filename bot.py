import logging
import nest_asyncio
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import requests
import time

# تطبيق nest_asyncio
nest_asyncio.apply()

# إعدادات API والبوت
API_KEY = '1925045198'
BOT_TOKEN = "5175709686:AAEs5-jvaCRmoEK8d0Ix8GUHj2ze3uJ0Abk"
BASE_URL = 'https://smartclownxfreefireinfo.vercel.app/like'
CHANNEL_ID = -1002349706113  # معرف القناة
CHANNEL_LINK = "https://t.me/l7aj_ff_group"

# الدول والمناطق مع نوع الخادم وعدد الخوادم لكل منطقة
REGIONS = {
    "ind": {"name": "الهند", "servers": 2},
    "sea": [
        {"name": "بنغلاديش", "server": 2},
        {"name": "رابطة الدول المستقلة (CIS)", "server": 2},
        {"name": "أوروبا", "server": 2},
        {"name": "إندونيسيا", "server": 2},
        {"name": "الشرق الأوسط وأفريقيا", "server": 2},
        {"name": "باكستان", "server": 2},
        {"name": "سنغافورة", "server": 2},
        {"name": "تايلاند", "server": 2},
        {"name": "تايوان", "server": 2},
        {"name": "فيتنام", "server": 2},
    ],
    "us": [
        {"name": "البرازيل", "servers": 5},
        {"name": "أمريكا الشمالية", "servers": 5},
        {"name": "أمريكا الجنوبية (الإسبانية)", "servers": 5},
        {"name": "الولايات المتحدة", "servers": 5},
    ],
}

# تفعيل الـ logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# دالة معالجة النصوص لتجنب أخطاء MarkdownV2
def escape_markdown(text):
    """
    Escape MarkdownV2 reserved characters in the text.
    """
    return re.sub(r'([_*()~`>#+\-=|{}.!])', r'\\\1', text)

# وظيفة التحقق من انضمام المستخدم إلى القناة
async def is_user_in_channel(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# وظيفة إرسال الطلبات إلى الـ API
def send_request(uid, server_name, region_name, context, update):
    target_url = f"{BASE_URL}?uid={uid}&server_name={server_name}&key={API_KEY}"

    try:
        response = requests.get(target_url)
        response.raise_for_status()

        api_response = response.json()
        if api_response["status"] == 2:
            return f"لقد بلغت الحد اليومي عد غدا او ارسل UID  أخر \n\n""المطور @l7l7aj"
        else:
            result_message = (
                f"✅ تم العثور على خادم مناسب!\n"
                f"تهانينا! {api_response['PlayerNickname']}, تم إرسال {api_response['LikesGivenByAPI']} إعجابًا بنجاح!\n"
                f"UID: {api_response['UID']}\n"
                f"الإعجابات قبل الإرسال: {api_response['LikesbeforeCommand']}\n"
                f"الإعجابات بعد الإرسال: {api_response['LikesafterCommand']}\n"
                f"يرجى العودة بعد 24 ساعة لإرسال 100 إعجاب آخر!\n\n""المطور @l7l7aj"
            )
            return result_message

    except requests.exceptions.RequestException as e:
        print(f"⚠️ خطأ في الخادم {region_name} - {server_name}: {str(e)}")
        return None

# وظيفة العد التنازلي مع نسبة مئوية بجانب الشريط
# وظيفة العد التنازلي مع نسبة مئوية بجانب الشريط بطريقة سلسة
async def countdown_message(message, duration):
    for i in range(duration, 0, -1):
        completed = duration - i
        percentage = int((completed / duration) * 100)
        red_squares = '█' * completed
        black_squares = '▒' * i
        # تحديث الرسالة بشكل تدريجي مع التأثيرات
        await message.edit_text(
            f"⏳ انتظر، جاري التحقق من الخوادم... ({i} ثواني)\n\n"
            f"{red_squares}{black_squares} {percentage}%"
        )
        await asyncio.sleep(0.5)  # إضافة تأخير بين التحديثات لجعلها سلسة

# وظيفة تنفيذ طلبات الإعجابات
async def claim_likes(uid, update: Update, context: CallbackContext):
    if not uid:
        await update.message.reply_text("خطأ: يجب إدخال UID صالح.")
        return

    message = await update.message.reply_text("⏳ انتظر، جاري التحقق من الخوادم...\n\n""المطور @l7l7aj")
    await countdown_message(message, 15)

    for region, data in REGIONS.items():
        if isinstance(data, list):
            for country in data:
                server_name = f"{region}2"
                result = send_request(uid, server_name, country["name"], context, update)
                if result:
                    await message.delete()
                    await update.message.reply_text(result)
                    return
        else:
            for server in range(1, data["servers"] + 1):
                server_name = f"{region}{server}"
                result = send_request(uid, server_name, data["name"], context, update)
                if result:
                    await message.delete()
                    await update.message.reply_text(result)
                    return

    await message.edit_text("❌ لم يتم العثور على خادم متاح.")

# وظيفة بدء البوت
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if await is_user_in_channel(user_id, context.bot):
        await update.message.reply_text("مرحبا! قم بإرسال UID  الخاص بك  لإرسال 100 لايك ✔️.")
    else:
        msg = await update.message.reply_text(
            "عليك أولا الأنضمام الى المجوعة ✨️🙂:\n\n"
  
            f"[انقر هنا للانضمام]({CHANNEL_LINK})\n\n"
            
            "إنقر على /start\n\n",
            parse_mode="MarkdownV2"
        )

# معالجة الرسائل
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not await is_user_in_channel(user_id, context.bot):
        msg = await update.message.reply_text(
            "عليك أولا الأنضمام الى المجوعة ✨️🙂:\n\n"
  
            f"[انقر هنا للانضمام]({CHANNEL_LINK})\n\n"
            
            "إنقر على /start\n\n",
            parse_mode="MarkdownV2"
        )
        return

    uid = update.message.text.strip()
    if uid.lower() == "exit":
        await update.message.reply_text("جاري الخروج... وداعًا!")
        return
    await claim_likes(uid, update, context)

# الوظيفة الرئيسية
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
