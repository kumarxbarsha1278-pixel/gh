import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8142270559:AAE9kfW5k7ZsA43C2A4pXXwELr7nF9vhEII"
GITHUB_TOKEN = "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"
GITHUB_REPO = "kumarxbarsha1278-pixel/gh"
# ---------------------

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /run command and dispatches to GitHub Actions."""
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ **Invalid Format.**\n\nUse: `/run <IP> <PORT> <TIME>`\nExample: `/run 1.1.1.1 80 60`"
        )
        return

    ip, port, time_arg = context.args[0], context.args[1], context.args[2]

    await update.message.reply_text(
        f"⚡ **Codespace dispatching task to GitHub Actions...**\n\n🌐 **IP:** {ip}\n🔌 **Port:** {port}\n⏱️ **Time:** {time_arg} seconds"
    )

    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {
        "event_type": "telegram_trigger",
        "client_payload": {"ip": ip, "port": port, "time": time_arg}
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 204:
            await update.message.reply_text("🚀 **Success:** GitHub VM has started the `./ARK` operation!")
        else:
            await update.message.reply_text(f"❌ **GitHub Connection Error ({response.status_code}):**\n`{response.text}`")
    except Exception as e:
        await update.message.reply_text(f"💥 **Failed to communicate with GitHub:**\n`{e}`")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 **ARK Codespace Bot Dispatcher Active!**\n\nType:\n`/run <IP> <PORT> <TIME>`")

def main():
    print("--> Initializing Telegram Connection from Codespace...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("run", run_command))
    application.run_polling()

if __name__ == "__main__":
    main()
