import os
import asyncio
import threading
import time
import json
from flask import Flask, request, jsonify, Response

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

app = Flask(__name__)
MAIN_LOOP = None
BOT_READY = threading.Event()

# গ্লোবাল ভেরিয়েবল
CURRENT_TEAM_CODE = None
GLOBAL_KEY = None
GLOBAL_IV = None
LAST_REQUEST_TIME = 0 # 🛑 স্প্যামিং আটকানোর কুলডাউন

# ==================== ইমোট লিস্ট ====================
EMOTES = [
    {"Number": "1",  "Id": "912055001"},
    {"Number": "2",  "Id": "909000068"},
    {"Number": "3",  "Id": "909000075"},
    {"Number": "4",  "Id": "909040010"},
    {"Number": "5",  "Id": "909000081"},
    {"Number": "6",  "Id": "909039011"},
    {"Number": "7",  "Id": "909000085"},
    {"Number": "8",  "Id": "909000090"},
    {"Number": "9",  "Id": "909000098"},
    {"Number": "10", "Id": "909035007"},
    {"Number": "11", "Id": "909037011"},
    {"Number": "12", "Id": "909041005"},
    {"Number": "13", "Id": "909038010"},
    {"Number": "14", "Id": "909038012"},
    {"Number": "15", "Id": "909045001"},
    {"Number": "16", "Id": "909049010"},
    {"Number": "17", "Id": "909051003"},
    {"Number": "18", "Id": "909042008"},
    {"Number": "19", "Id": "909033001"},
    {"Number": "20", "Id": "909049012"},
    {"Number": "21", "Id": "909000002"},
]

# ==================== গোল্ডেন HTML ড্যাশবোর্ড ====================
HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DARK EMOTE - Golden Panel</title>
    <style>
        * { box-sizing: border-box; }
        body {
            background-color: #0a0a0a;
            color: #FFD700;
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: rgba(15, 15, 15, 0.95);
            border: 2px solid #FFD700;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.3);
            border-radius: 12px;
            padding: 20px;
            width: 100%;
            max-width: 420px;
            margin-top: 20px;
        }
        h2 {
            text-align: center;
            color: #FFD700;
            text-shadow: 0 0 10px #FFD700;
            margin: 0 0 10px 0;
            font-size: 18px;
        }
        .credit {
            text-align: center;
            font-size: 11px;
            color: #DAA520;
            margin-bottom: 15px;
        }
        .divider { height: 1px; background: #FFD700; margin: 15px 0; opacity: 0.3; }
        
        .input-group { margin-bottom: 12px; }
        label { display: block; font-size: 12px; color: #DAA520; margin-bottom: 4px; }
        input {
            width: 100%; padding: 10px; background: #000; border: 1px solid #FFD700;
            color: #FFD700; border-radius: 6px; font-family: 'Courier New', Courier, monospace; outline: none;
        }
        input:focus { box-shadow: 0 0 10px #FFD700; }
        
        button.login-btn {
            width: 100%; padding: 12px; background: #FFD700; color: #000;
            border: none; border-radius: 6px; font-weight: bold; cursor: pointer;
            font-family: 'Courier New', Courier, monospace; font-size: 14px; margin-top: 5px;
            transition: 0.3s;
        }
        button.login-btn:hover { background: #FFA500; transform: scale(1.02); }

        .status { text-align: center; font-size: 13px; margin-top: 10px; min-height: 20px; font-weight: bold;}

        .grid-title { text-align: center; font-size: 12px; color: #FFD700; margin-bottom: 10px; font-weight: bold; }
        .emote-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
        .emote-btn {
            background: #111; border: 1px solid #FFD700; color: #FFD700;
            aspect-ratio: 1 / 1; border-radius: 6px; cursor: pointer;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            transition: all 0.15s ease; font-family: 'Courier New', Courier, monospace;
            box-shadow: inset 0 0 5px rgba(255,215,0,0.1);
        }
        .emote-btn .num { font-size: 16px; font-weight: bold; }
        .emote-btn .id { font-size: 8px; margin-top: 3px; opacity: 0.7; }
        .emote-btn:hover { background: #FFD700; color: #000; box-shadow: 0 0 15px #FFD700; }
        .emote-btn:active { transform: scale(0.95); }
        .emote-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="container">
        <h2>👑 DARK EMOTE CONTROL 👑</h2>
        <div class="credit">POWERED BY DARK MASTER</div>

        <!-- লগইন সেকশন -->
        <div id="login-section">
            <div class="input-group">
                <label>ACCOUNT UID:</label>
                <input type="text" id="acc_uid" placeholder="Enter Account UID">
            </div>
            <div class="input-group">
                <label>PASSWORD:</label>
                <input type="password" id="acc_pass" placeholder="Enter Password">
            </div>
            <button class="login-btn" onclick="loginAccount()">🔐 LOGIN ACCOUNT</button>
            <div id="login-status" class="status"></div>
        </div>

        <div class="divider"></div>

        <!-- ইমোট সেকশন (লগইনের আগে লকড) -->
        <div id="emote-section" style="opacity: 0.5; pointer-events: none;">
            <div class="input-group">
                <label>TEAM CODE:</label>
                <input type="text" id="tc" placeholder="Enter Team Code">
            </div>
            <div class="input-group">
                <label>TARGET UID:</label>
                <input type="text" id="uid1" placeholder="Enter Target UID">
            </div>
            
            <div class="grid-title">// SELECT EMOTE //</div>
            <div class="emote-grid" id="emoteGrid"></div>
            <div id="status" class="status"></div>
        </div>
    </div>

    <script>
        const EMOTES = {{ EMOTES_JSON | safe }};
        const grid = document.getElementById('emoteGrid');
        
        EMOTES.forEach(e => {
            const btn = document.createElement('button');
            btn.className = 'emote-btn';
            btn.innerHTML = `<span class="num">${e.Number}</span><span class="id">${e.Id}</span>`;
            btn.onclick = () => playEmote(e.Id, btn);
            grid.appendChild(btn);
        });

        async function loginAccount() {
            const uid = document.getElementById('acc_uid').value.trim();
            const pass = document.getElementById('acc_pass').value.trim();
            const statusDiv = document.getElementById('login-status');

            if (!uid || !pass) {
                statusDiv.style.color = "#ff3333";
                statusDiv.innerText = "❌ Missing UID or Password!";
                return;
            }

            statusDiv.style.color = "#FFD700";
            statusDiv.innerText = "⏳ Logging in... Please wait.";
            
            try {
                const r = await fetch(`/login?uid=${encodeURIComponent(uid)}&pass=${encodeURIComponent(pass)}`);
                const d = await r.json();
                if (d.status === 'success') {
                    statusDiv.style.color = "#00ff66";
                    statusDiv.innerText = "✅ " + d.msg;
                    // ইমোট সেকশন আনলক করা
                    document.getElementById('emote-section').style.opacity = "1";
                    document.getElementById('emote-section').style.pointerEvents = "auto";
                } else {
                    statusDiv.style.color = "#ff3333";
                    statusDiv.innerText = "❌ " + d.msg;
                }
            } catch (err) {
                statusDiv.style.color = "#ff3333";
                statusDiv.innerText = "❌ Server Error!";
            }
        }

        async function playEmote(emoteId, btn) {
            const tc = document.getElementById('tc').value.trim();
            const uid1 = document.getElementById('uid1').value.trim();
            const statusDiv = document.getElementById('status');

            if (!tc || !uid1) {
                statusDiv.style.color = "#ff3333";
                statusDiv.innerText = "[!] Missing Team Code or UID!";
                return;
            }

            statusDiv.style.color = "#FFD700";
            statusDiv.innerText = `[*] Sending Emote ${emoteId}...`;

            // 🛑 বাটন ডিজেবল (স্প্যামিং আটকাতে)
            btn.disabled = true; 

            try {
                const r = await fetch(`/trigger?tc=${encodeURIComponent(tc)}&uid1=${encodeURIComponent(uid1)}&emote_id=${encodeURIComponent(emoteId)}`);
                const d = await r.json();
                if (d.status === 'success') {
                    statusDiv.style.color = "#00ff66";
                    statusDiv.innerText = `[+] SUCCESS: Emote ${emoteId} sent!`;
                } else {
                    statusDiv.style.color = "#ff3333";
                    statusDiv.innerText = "[!] FAILED: " + (d.message || "Unknown error");
                }
            } catch (err) {
                statusDiv.style.color = "#ff3333";
                statusDiv.innerText = "[!] NETWORK ERROR!";
            } finally {
                // 🛑 ১০ সেকেন্ড পর আবার ক্লিক করা যাবে (ব্যান এড়াতে)
                setTimeout(() => { btn.disabled = false; }, 10000);
            }
        }
    </script>
</body>
</html>
'''

# ==================== ইভেন্ট লুপ ====================
def _run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# ==================== লগইন প্রসেস ====================
async def login_and_connect(uid, pw, region):
    global GLOBAL_KEY, GLOBAL_IV
    print(f"[*] Logging in UID: {uid}...")
    result = await login_engine.do_login(uid, pw, region)
    
    if not result:
        print("[-] Login failed!")
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

# ==================== ইমোট পাঠানোর লজিক ====================
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
        
        # 🛑 টিমে ঢোকার পর ৫ সেকেন্ড অপেক্ষা
        await asyncio.sleep(5.0) 

    # ২. ইমোট পাঠানো
    sent = 0
    print(f"[*] Sending Emote {emoteid} to {uids}")
    for uid in uids:
        pkt = await Emote_k(int(uid), int(emoteid), GLOBAL_KEY, GLOBAL_IV, bot_core.region)
        
        bot_core.online_writer.write(pkt)
        await bot_core.online_writer.drain()
        sent += 1
        
        # 🛑 প্রতিটি ইমোটের মাঝে ৩ সেকেন্ড বিরতি
        await asyncio.sleep(3.0)

    return sent

# ==================== Flask রুট ====================
@app.route("/")
def index():
    return Response(HTML_CONTENT.replace("{{ EMOTES_JSON | safe }}", json.dumps(EMOTES)), mimetype="text/html")

@app.route("/login")
def login_api():
    uid = request.args.get("uid")
    pw = request.args.get("pass")
    
    if not uid or not pw:
        return jsonify({"status": "error", "msg": "UID and Pass required"}), 400

    async def task():
        return await login_and_connect(uid, pw, "BD")

    fut = asyncio.run_coroutine_threadsafe(task(), MAIN_LOOP)
    try:
        success = fut.result(timeout=25)
        if success:
            return jsonify({"status": "success", "msg": "Account Logged In Successfully!"})
        else:
            return jsonify({"status": "error", "msg": "Login failed. Check UID/Pass."}), 401
    except Exception as e:
        return jsonify({"status": "error", "msg": f"Timeout: {e}"}), 500

@app.route("/trigger")
def trigger():
    global LAST_REQUEST_TIME
    if not BOT_READY.is_set() or MAIN_LOOP is None:
        return jsonify({"status": "error", "message": "Please login first."}), 503

    # 🛑 কুলডাউন সিস্টেম (১০ সেকেন্ডের কম সময়ে রিকোয়েস্ট দিলে ব্লক করবে)
    current_time = time.time()
    if current_time - LAST_REQUEST_TIME < 10: 
        return jsonify({"status": "error", "message": "⚠️ Please wait 10 seconds before sending another emote."}), 429
    
    LAST_REQUEST_TIME = current_time

    tc = request.args.get("tc", "").strip()
    uid1 = request.args.get("uid1", "").strip()
    emote_id = request.args.get("emote_id", "").strip()

    if not all([tc, uid1, emote_id]):
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    async def task():
        try:
            n = await do_emote_safe(tc, [uid1], emote_id)
            return {"status": "success", "message": "Emote triggered"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    fut = asyncio.run_coroutine_threadsafe(task(), MAIN_LOOP)
    try:
        result = fut.result(timeout=20)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Timeout: {e}"}), 500

# ==================== চালু করা ====================
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    MAIN_LOOP = loop
    threading.Thread(target=_run_loop, args=(loop,), daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    print(f"[*] Public Web API starting on port {port}...")
    app.run(host="0.0.0.0", port=port, threaded=True)
