from aiogram import Bot

from config import BOT_TOKEN, NOTIFICATION_CHAT_ID


bot = Bot(token=BOT_TOKEN)


async def send_notification(
    sender_name: str,
    sender_username: str | None,
    message: str,
):
    username = (
        f"@{sender_username}"
        if sender_username
        else "Username yo'q"
    )

    text = (
        "🔔 YANGI XABAR\n\n"
        f"👤 Ism: {sender_name}\n"
        f"📱 Username: {username}\n"
        f"💬 Xabar: {message}\n\n"
        "⚠️ Javob berishingiz kerak."
    )

    try:
        await bot.send_message(
            chat_id=NOTIFICATION_CHAT_ID,
            text=text,
        )

        print("📨 Account #2 ga notification yuborildi.")

    except Exception as error:
        print(
            f"❌ Notification yuborishda xato: "
            f"{type(error).__name__}: {error}"
        )