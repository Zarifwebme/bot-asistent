import asyncio
import logging

from telethon import TelegramClient, events
from telethon.errors import (
    AuthKeyUnregisteredError,
    FloodWaitError,
    RPCError,
)

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from services.database import (
    has_auto_replied,
    init_db,
    mark_auto_replied,
)
from services.notifier import send_notification


# -----------------------------------------
# LOGGING
# -----------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# -----------------------------------------
# TELEGRAM CLIENT
# -----------------------------------------

client = TelegramClient(
    "telegram_user",
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
)


# -----------------------------------------
# AUTO REPLY
# -----------------------------------------

async def send_auto_reply(
    event,
    chat_id: int,
):
    try:
        logger.info(
            "⏳ Chat %s uchun 5 soniya kutilyapti...",
            chat_id,
        )

        await asyncio.sleep(5)

        await event.reply(
            "Assalomu alaykum, siz bilan tez orada bog‘lanaman."
        )

        mark_auto_replied(chat_id)

        logger.info(
            "✅ Auto-reply yuborildi. Chat ID: %s",
            chat_id,
        )

    except FloodWaitError as error:
        logger.warning(
            "⚠️ Telegram FloodWait: %s soniya",
            error.seconds,
        )

        await asyncio.sleep(error.seconds)

        try:
            await event.reply(
                "Assalomu alaykum, siz bilan tez orada bog‘lanaman."
            )

            mark_auto_replied(chat_id)

        except Exception as retry_error:
            logger.error(
                "❌ Auto-reply retry xatosi: %s",
                retry_error,
            )

    except Exception as error:
        logger.error(
            "❌ Auto-reply xatosi | chat_id=%s | %s: %s",
            chat_id,
            type(error).__name__,
            error,
        )


# -----------------------------------------
# INCOMING MESSAGE
# -----------------------------------------

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):

    try:
        sender = await event.get_sender()

        name = sender.first_name or "Noma'lum"
        username = sender.username
        message = event.raw_text
        chat_id = event.chat_id

        logger.info(
            "🔔 YANGI XABAR | %s | %s | chat_id=%s",
            name,
            message,
            chat_id,
        )

        # ---------------------------------
        # NOTIFICATION
        # ---------------------------------

        try:
            await send_notification(
                sender_name=name,
                sender_username=username,
                message=message,
            )

        except Exception as error:
            logger.error(
                "❌ Notification handler xatosi: %s",
                error,
            )

        # ---------------------------------
        # AUTO REPLY
        # ---------------------------------

        if not has_auto_replied(chat_id):

            logger.info(
                "🆕 Bu chatga hali auto-reply yuborilmagan."
            )

            # 5 soniyalik task yaratamiz.
            #
            # Handlerning o'zi 5 soniya bloklanmaydi.
            asyncio.create_task(
                send_auto_reply(
                    event,
                    chat_id,
                )
            )

        else:
            logger.info(
                "ℹ️ Auto-reply oldin yuborilgan. "
                "Chat ID: %s",
                chat_id,
            )

    except Exception as error:
        logger.exception(
            "❌ Message handlerda kutilmagan xato: %s",
            error,
        )


# -----------------------------------------
# START CLIENT
# -----------------------------------------

async def start_client():

    init_db()

    logger.info("🚀 Telegram assistant ishga tushmoqda...")

    try:

        await client.start()

        logger.info("✅ Telegram account ulandi.")
        logger.info("👂 Yangi xabarlar kutilmoqda...")

        await client.run_until_disconnected()

    except AuthKeyUnregisteredError:

        logger.critical(
            "❌ TELEGRAM SESSION INVALID!\n"
            "telegram_user.session Telegram tomonidan "
            "endi tan olinmayapti.\n"
            "Serverda qayta login qilish kerak."
        )

        raise

    except FloodWaitError as error:

        logger.warning(
            "⚠️ Telegram FloodWait: %s soniya",
            error.seconds,
        )

        await asyncio.sleep(error.seconds)

    except RPCError as error:

        logger.error(
            "❌ Telegram RPC error: %s",
            error,
        )

        raise

    except Exception as error:

        logger.exception(
            "❌ Telegram client xatosi: %s",
            error,
        )

        raise

    finally:

        if client.is_connected():

            await client.disconnect()

            logger.info(
                "🔌 Telegram client yopildi."
            )