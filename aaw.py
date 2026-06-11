import logging
import subprocess
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==================== CONFIGURATION ====================
# Your Telegram Bot Token
BOT_TOKEN = "8142270559:AAFnl0FRwHdoeuFCRy9M52shitsSn6-FPO4"

# For security, restrict access to specific Telegram User IDs.
# Add your own numeric Telegram ID to this list. Leave empty [] to allow anyone (NOT recommended).
ALLOWED_USERS = []  # e.g., [123456789, 987654321]

# Path to the binary executable you want to run
BINARY_PATH = "./neo4"
# =======================================================

# Enable detailed logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Regular expression to validate standard IPv4 addresses or domain names
IP_REGEX = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$|^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcoming message when the user sends /start."""
    user = update.effective_user
    logger.info(f"User {user.first_name} (ID: {user.id}) started the bot.")
    
    welcome_text = (
        "🤖 *Welcome to the Command Executor Bot!*\n\n"
        "To run the command, use:\n"
        "`/run <ip> <port> <time>`\n\n"
        "Example:\n"
        "`/run 1.1.1.1 80 60`"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Executes the ./dd binary with user arguments."""
    user = update.effective_user
    user_id = user.id

    # Security check: Limit usage to whitelisted users if ALLOWED_USERS is defined
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        logger.warning(f"Unauthorized access attempt by {user.full_name} (ID: {user_id})")
        await update.message.reply_text("⛔ You are not authorized to use this bot.")
        return

    # Argument validation: Require exactly 3 parameters (ip, port, time)
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ *Invalid Arguments!*\n"
            "Usage: `/run <ip> <port> <time>`\n"
            "Example: `/run 1.1.1.1 80 60`",
            parse_mode="Markdown"
        )
        return

    ip, port, duration = context.args

    # Strict Validation to avoid Shell Injection and bad parameters
    if not IP_REGEX.match(ip):
        await update.message.reply_text("❌ *Invalid IP Address* or domain format.")
        return

    if not port.isdigit() or not (1 <= int(port) <= 65535):
        await update.message.reply_text("❌ *Invalid Port*. Must be a number between 1 and 65535.")
        return

    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ *Invalid Duration*. Must be a positive integer.")
        return

    # Check if the binary executable exists in the path
    if not os.path.exists(BINARY_PATH):
        await update.message.reply_text(f"❌ Error: Binary file `{BINARY_PATH}` could not be found.")
        return

    # Notify user that the execution started
    status_msg = await update.message.reply_text(
        f"⏳ *Running execution...*\n"
        f"Target: `{ip}:{port}`\n"
        f"Duration: `{duration}` seconds",
        parse_mode="Markdown"
    )

    try:
        # Construct the execution command securely (as a list, preventing shell parsing issues)
        cmd = [BINARY_PATH, ip, port, duration]
        
        logger.info(f"User {user_id} executing: {' '.join(cmd)}")

        # Run process asynchronously with a safeguard timeout (e.g., duration + 10 seconds)
        max_timeout = int(duration) + 10
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=max_timeout
        )

        # Build output message
        if process.returncode == 0:
            stdout_preview = process.stdout[:3000] if process.stdout else "No standard output generated."
            response = (
                f"✅ *Execution Finished successfully!*\n\n"
                f"*Output:*\n```\n{stdout_preview}\n```"
            )
        else:
            stderr_preview = process.stderr[:3000] if process.stderr else "No error output details."
            response = (
                f"⚠️ *Finished with non-zero exit code ({process.returncode}):*\n\n"
                f"*Error log:*\n```\n{stderr_preview}\n```"
            )

        await status_msg.edit_text(response, parse_mode="Markdown")

    except subprocess.TimeoutExpired:
         await status_msg.edit_text("⏳ *Execution Timed Out.* The operation took too long to complete.", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        await status_msg.edit_text(f"❌ *Failed to execute process:*\n`{str(e)}`", parse_mode="Markdown")

def main() -> None:
    """Configures and runs the Telegram Bot."""
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("CRITICAL: Please specify your bot token in the bot.py file.")
        return

    # Initialize the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_command))

    # Begin polling telegram update server
    logger.info("Bot starting up. Listening to updates...")
    application.run_polling()

if __name__ == "__main__":
    main()
