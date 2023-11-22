import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from dotenv import load_dotenv
import os
import subprocess


load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text()


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    action_data = query.data.split()
    action = action_data[0]
    
    await query.answer()

    username = action_data[1]
    user_host = action_data[2]
    
    if action[0:9] == "kick_user":
        subprocess.run(["./scripts/kick_user.sh", username])
        await update.effective_message.reply_text("User has been successfully kicked")
        
    elif action[0:8] == "ban_user":
        result = subprocess.run(["./scripts/ban_user.sh", username, user_host], capture_output=True)
        await update.effective_message.reply_text(f"{result.stdout.decode()}\n{result.stderr.decode()}")

async def unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_ip = context.args[0] if context.args else None

    if user_ip:
        process = subprocess.run(["sudo", "./scripts/unban_user.sh", user_ip], capture_output=True)

        if process.returncode == 0:
            response_message = f"User with IP {user_ip} has been successfully unbanned."
        else:
            response_message = f"Failed to unban user with IP {user_ip}. Error output:\n{process.stderr.decode()}"
    else:
        response_message = "Please provide the IP address of the user to unban."

    await update.message.reply_text(response_message)

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(CommandHandler("unban", unban_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()