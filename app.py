import os
import asyncio
import threading
import time
from flask import Flask, request, jsonify

import login_engine
import bot_core
from bot_core import (
    TcPOnLine, 
    TcPChaT, 
    build_ob55_online_auth, 
    create_auth_token_chat,
    JoinSq_original, 
    ExiT
)
from xC4 import Emote_k

# ==================== কনফিগারেশন ====================
# আপনার অ্যাকাউন্টের তথ্য
BOT_UID = os.environ.get("BOT_UID", "8418656473")
# এখানে একটি বাড়তি ডাবল কোট (") ছিল, সেটি ঠিক করা হয়েছে
BOT_PW  = os.environ.get("BOT_PW",  "29E1148FAA232BF1345320077DF231E8470D740C8E5B22EE31B812AB8B76AB2E")
REGION  = os.environ.get("REGION",  "BD")

PORT    = int(os.environ.get("PORT", 10000))

app = Flask(__name__)
MAIN_LOOP = None
BOT_READY = threading.Event()

# গ্লোবাল ভেরিয়েবল
CURRENT_TEAM_CODE = None
GLOBAL_KEY = None
GLOBAL_IV = None

# ==================== ইভেন্ট লুপ ====================
def _run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# ==================== লগইন প্রসেস ====================
async def login_and_connect():
    global GLOBAL_KEY, GLOBAL_IV
    print("[*] Starting login...")
    result = await login_engine.do_login(BOT_UID, BOT_PW, REGION)
    
    if not result:
        print("[-] Login failed, retry in 10s...")
        return False

    bot_core.bot_uid = result["bot_uid"]
    bot_core.ToKen   = result["token"]
    bot_core.region  = result["region"]
    
    GLOBAL_KEY = result["key"]
    GLOBAL_IV  = result["iv"]
    bot_core.key = GLOBAL_KEY
    bot_core.iv = GLOBAL_IV

    timestamp = result["timestamp"]
    
    print(f"[+] UID: {result['bot_uid']} | Region: {result['region']} | Name: {result['account_name']}")

    ChatAutH = create_auth_token_chat(
        int(result["bot_uid"]), result["token"], int(timestamp), GLOBAL_KEY, GLOBAL_IV
    )
    OnlineAutH, _ = build_ob55_online_auth(
        int(result["bot_uid"]), result["token"], int(timestamp), GLOBAL_KEY, GLOBAL_IV
    )

    ready_event = asyncio.Event()
    asyncio.create_task(
        TcPChaT(result["chat_ip"], result["chat_port"], ChatAutH, GLOBAL_KEY, GLOBAL_IV, ready_event, result["region"])
    )
    await ready_event.wait()
    await asyncio.sleep(1)
    asyncio.create_task(
        TcPOnLine(result["online_ip"], result["online_port"], GLOBAL_KEY, GLOBAL_IV, OnlineAutH)
    )

    BOT_READY.set()
    print(f"[+] Bot Online! UID: {result['bot_uid']}")
    return True

async def main_loop():
    while True:
        try:
            ok = await login_and_connect()
            if ok:
                while True:
                    await asyncio.sleep(3600)
        except Exception as e:
            print(f"[!] Error: {e} -> Restarting in 5s...")
            await asyncio.sleep(5)

# ==================== ইমোট পাঠানোর মেইন লজিক ====================
async def do_emote_safe(teamcode, uids, emoteid):
    global CURRENT_TEAM_CODE
    
    if not GLOBAL_KEY or not bot_core.online_writer:
        raise RuntimeError("Bot is not connected to online server.")

    # ১. টিম জয়েন
    if CURRENT_TEAM_CODE != str(teamcode):
        print(f"[*] Joining Team: {teamcode}")
        join_pkt = await JoinSq_original(teamcode, GLOBAL_KEY, GLOBAL_IV)
        
        bot_core.online_writer.write(join_pkt)
        await bot_core.online_writer.drain()
        CURRENT_TEAM_CODE = str(teamcode)
        
        # প্লেয়ার ঢোকার জন্য অপেক্ষা (ব্যান এড়াতে ৩ সেকেন্ড)
        await asyncio.sleep(3.0) 

    # ২. ইমোট পাঠানো
    sent = 0
    print(f"[*] Sending Emote {emoteid} to {uids}")
    for uid in uids:
        pkt = await Emote_k(int(uid), int(emoteid), GLOBAL_KEY, GLOBAL_IV, bot_core.region)
        
        bot_core.online_writer.write(pkt)
        await bot_core.online_writer.drain()
        sent += 1
        
        # স্বাভাবিক গতিতে ইমোট পাঠানোর জন্য ০.৫ সেকেন্ড বিরতি
        await asyncio.sleep(0.5)

    return sent

# ==================== Flask API ====================
@app.route("/")
def home():
    return "FF Emote API is Running Publicly!"

@app.route("/emote")
def emote_api():
    if not BOT_READY.is_set() or MAIN_LOOP is None:
        return jsonify({"status": "error", "msg": "Bot is not ready yet. Please wait..."}), 503

    teamcode = request.args.get("teamcode")
    emoteid  = request.args.get("emoteid")
    if not teamcode or not emoteid:
        return jsonify({"status": "error", "msg": "teamcode and emoteid are required"}), 400

    uids = [request.args.get(f"uid{i}") for i in range(1, 5) if request.args.get(f"uid{i}")]
    if not uids:
        return jsonify({"status": "error", "msg": "uid1 is required"}), 400

    async def task():
        try:
            n = await do_emote_safe(teamcode, uids, emoteid)
            return {"status": "success", "sent": n, "targets": uids, "emote": emoteid}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

    fut = asyncio.run_coroutine_threadsafe(task(), MAIN_LOOP)
    try:
        return jsonify(fut.result(timeout=30))
    except Exception as e:
        return jsonify({"status": "error", "msg": f"Timeout: {e}"}), 500

# ==================== চালু করা ====================
# Vercel/Cloud প্ল্যাটফর্মের জন্য অ্যাপ ভেরিয়েবল নিশ্চিত করা হলো
app = app 

loop = asyncio.new_event_loop()
MAIN_LOOP = loop
threading.Thread(target=_run_loop, args=(loop,), daemon=True).start()
asyncio.run_coroutine_threadsafe(main_loop(), loop)

if __name__ == "__main__":
    print(f"[*] Public Web API starting on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, threaded=True)
