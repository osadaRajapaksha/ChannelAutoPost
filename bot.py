import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def health():
    return 'OK', 200

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    print(f"✅ Dummy health server running on port {port}")
    app.run(host="0.0.0.0", port=port, threaded=True)

threading.Thread(target=run_health_server, daemon=True).start()




















# ChannelAutoPost – Modified for 10→10 Mirroring
# Based on ChannelAutoForwarder by @xditya
# Edited for 1-to-1 channel mirroring (fresh repost, not forward)

import logging
from telethon import TelegramClient, events, Button
from decouple import config

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = logging.getLogger("ChannelAutoPost")

log.info("Starting Channel AutoPost Bot (1→1 mirror mode)...")

# Telegram credentials from .env
try:
    apiid = config("APP_ID", cast=int)
    apihash = config("API_HASH")
    bottoken = config("BOT_TOKEN")
    datgbot = TelegramClient(None, apiid, apihash).start(bot_token=bottoken)
except Exception as exc:
    log.error("Environment vars missing or invalid!")
    log.error(exc)
    exit()

# -------------- YOUR 10→10 CHANNEL MAPPING HERE -----------------
# Example format:
CHANNEL_PAIRS = {
    -1002867578605: [-1002815938247, -1002572158430, -1002854405050, -1002482136007],
    -1002823841610: [-1002411969209, -1002694895406, -1002494024602, -1002614235924],
    -1002813320490: [-1002625348452, -1002545798162, -1002777150597, -1002604468355],
    -1002794743739: [-1002791728876, -1002539168678, -1002579335139, -1002721387416],
    -1002687548561: [-1002766645721, -1002709413738, -1002886635890, -1002700190202],
    
    -1002669307492: [-1002832455792, -1002848346313, -1002581483887, -1002471457394, -1002851487698, -1002517724206, -1002741175244, -1002560358130],
    -1002786375612: [-1002721085921, -1002760212032, -1002719975805, -1002842946977, -1002692951426, -1002568198343, -1002847865886, -1002767111102],
    -1002843418789: [-1002840470350, -1002852120799, -1002761646562, -1002726706987, -1002638090439, -1002703462504, -1002586744088, -1002692833053],
    -1002792845679: [-1002895365275, -1002849482926, -1002797197515, -1002847217737, -1002790865688, -1002853991470, -1002611692708, -1002848754081],
    -1002392351777: [-1002702251010, -1002803721478, -1002678915086, -1002547373872, -1002577370776, -1002853990394, -1002858090540, -1002791271972, -1002518645730],
    
    
}
# ---------------------------------------------------------------

# /start command
@datgbot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        f"Hi `{event.sender.first_name}`!\n\n"
        f"I’m a channel auto-post bot running in 1→1 mirror mode.\n"
        f"Messages from 10 source channels will be sent freshly to 10 targets.\n\n"
        f"Use /help for more info.",
        buttons=[
            Button.url("Repo", url="https://github.com/xditya/ChannelAutoForwarder"),
            Button.url("Developer", url="https://xditya.me"),
        ],
        link_preview=False,
    )

# /help command
@datgbot.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    await event.reply(
        "**Help — 1→1 Channel Mirroring Bot**\n\n"
        "This bot listens to multiple source channels and sends their posts freshly to corresponding target channels.\n\n"
        "Example mapping:\n"
        "`src1 → dest1`, `src2 → dest2`, etc.\n\n"
        "No 'forwarded from' tag — posts look original.\n\n"
        "Make sure the bot is an **admin in both source and target channels.**"
    )




import asyncio
import random


@datgbot.on(events.NewMessage(incoming=True, chats=list(CHANNEL_PAIRS.keys())))
async def mirror_message(event):
    # Skip messages sent by this bot
    if event.out or event.message.out:
        return

    src = event.chat_id
    dests = CHANNEL_PAIRS.get(src)
    if not dests:
        return

    # Support one→many (space-separated IDs)
    if isinstance(dests, str):
        dests = [int(x) for x in dests.split()]
    elif isinstance(dests, int):
        dests = [dests]

    # ✅ Fetch full message to ensure entities (bold, italic, quote, spoiler) are loaded
    try:
        full_msg = await datgbot.get_messages(src, ids=event.id)
    except Exception as e:
        log.error(f"Could not fetch full message from {src}: {e}")
        return

    for dest in dests:
        try:
            if full_msg.poll:
                log.info(f"Skipping poll message in {src}")
                continue

            # --- Handle text/media while preserving Telegram formatting ---
            if full_msg.media:  # photo, video, etc.
                await datgbot.send_file(
                    dest,
                    full_msg.media,
                    caption=full_msg.message or "",
                    entities=full_msg.entities,
                    link_preview=False
                )
            elif full_msg.message:
                await datgbot.send_message(
                    dest,
                    full_msg.message,
                    entities=full_msg.entities,
                    link_preview=False
                )
            else:
                log.info(f"Unhandled message type from {src}")
                continue

            log.info(f"✅ Mirrored message from {src} → {dest}")

            # Random delay (5–10 s + jitter)
            delay = random.uniform(5, 10) + random.uniform(-0.4, 0.4)
            delay = max(0, delay)
            log.info(f"⏳ Waiting {delay:.2f}s before next send...")
            await asyncio.sleep(delay)

        except Exception as e:
            log.error(f"❌ Failed to mirror message from {src} → {dest}: {e}")









log.info("Bot is now running. Listening for new messages...")
datgbot.run_until_disconnected()

