# ═══════════════════════════════════════════════════════════════
# bot_core.py — DARK MASTER TCP BOT (FULL & FIXED)
# Dev: DARK MASTER | TG: https://t.me/dark_master
# ═══════════════════════════════════════════════════════════════

import asyncio, random, json, os, time
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from xC4 import *
from xP import JoinSq, OpenCh, MsqSq, ExitSq
from byte import Encrypt_ID, encrypt_api
from Pb2 import DEcwHisPErMsG_pb2, sQ_pb2

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════════════════
# CREDIT
# ═══════════════════════════════════════════════════════════════
CREDIT_NAME = "DARK MASTER"
CREDIT_DEV  = "DARK MASTER"
CREDIT_TG   = "https://t.me/dark_master"

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOTES_PATH       = os.path.join(BASE_DIR, "emotes.json")
EMOTE_MENU_PATH   = os.path.join(BASE_DIR, "emote_menu.json")
SINGLE_EMOTE_PATH = os.path.join(BASE_DIR, "singele_emote.json")
SPAM_TARGETS_FILE = os.path.join(BASE_DIR, "spam_targets.json")

# ═══════════════════════════════════════════════════════════════
# GLOBALS
# ═══════════════════════════════════════════════════════════════
online_writer = None
whisper_writer = None
spam_running = False
bot_uid = None
ToKen = None
region = None
admin_uid = "14624114894"

pending_ghost_future = None
ghost_team_id = None
ghost_squad_code = None

spm_tasks = {}
ban_task = None
ban_running = False
ban_targets = set()
evo_cycle_running = False
evo_cycle_task = None
freeze_running = False
freeze_task = None
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
msg_spam_running = False
msg_spam_task = None
mg_spam_task = None
reject_spam_running = False
reject_spam_task = None
emote_hijack = False
bot_enabled = True

EVO_IDS = [
    909055007, 909055004, 909055009, 909055002, 909055010,
    909055013, 909055007, 909055012, 909055006, 909055008, 
    909055005, 909054008, 909051010, 909050027, 909045009
]

# ═══════════════════════════════════════════════════════════════
# LOAD JSON FILES (ইমোটের সব কোড অক্ষত)
# ═══════════════════════════════════════════════════════════════
GENERAL_EMOTES_MAP = {}
EMOTE_MAP = {}
EMOTE_MENU = {}
SINGLE_EMOTES_MAP = {}

try:
    with open(EMOTES_PATH, "r", encoding="utf-8") as _f:
        _emote_list = json.load(_f)
    GENERAL_EMOTES_MAP = {str(item["Number"]): int(item["Id"]) for item in _emote_list}
    EMOTE_MAP = {int(item["Number"]): int(item["Id"]) for item in _emote_list}
    print(f"✅ Loaded {len(GENERAL_EMOTES_MAP)} emotes from emotes.json")
except Exception as _e:
    print(f"❌ emotes.json load error: {_e}")

try:
    with open(SINGLE_EMOTE_PATH, "r", encoding="utf-8") as _f:
        _single_list = json.load(_f)
    SINGLE_EMOTES_MAP = {str(item["Number"]): int(item["Id"]) for item in _single_list}
    print(f"✅ Loaded {len(SINGLE_EMOTES_MAP)} single emotes from singele_emote.json")
except Exception as _e:
    print(f"⚠️ singele_emote.json not loaded: {_e}")

try:
    with open(EMOTE_MENU_PATH, "r", encoding="utf-8") as _f:
        EMOTE_MENU = json.load(_f)
    print(f"✅ Loaded emote_menu.json")
except Exception as _e:
    print(f"⚠️ emote_menu.json not loaded: {_e}")

# ═══════════════════════════════════════════════════════════════
# NAME_EMOTES — সব ইমোট নাম (অক্ষত)
# ═══════════════════════════════════════════════════════════════
NAME_EMOTES = {
    "ak": 909000063, "scar": 909000068, "mp40": 909000075,
    "m1014": 909000081, "xm8": 909000085, "famas": 909000090,
    "ump": 909000098, "m1887": 909035007, "woodpecker": 909042008,
    "groza": 909041005, "m4a1": 909033001, "thompson": 909038010,
    "g18": 909038012, "parafal": 909045001, "p90": 909049010,
    "m60": 909051003, "fist": 909037011, "ring": 909050009,
    "heart": 909038004, "love": 909000010, "dance": 909000027,
    "hello": 909000001, "hi": 909000001, "money": 909000129,
    "lol": 909000002, "sad": 909038005, "angry": 909000014,
    "chicken": 909000006, "dab": 909000005, "selfie": 909000040,
    "shower": 909051004, "flower": 909051002, "petals": 909051013,
    "awm": 909055006,
}

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def load_spam_targets():
    if os.path.exists(SPAM_TARGETS_FILE):
        with open(SPAM_TARGETS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_spam_targets():
    with open(SPAM_TARGETS_FILE, "w") as f:
        json.dump(list(spam_targets), f)

spam_targets = load_spam_targets()

def get_random_color():
    colors = [
        "FFD700", "DAA520", "B8860B", "F0C040", "E6BE00",
        "FFCC33", "FFB300", "D4AF37", "CFB53B", "FFDF00",
        "FFE066", "F5C518", "E8B923", "C9A227", "B58B00"
    ]
    return random.choice(colors)

def get_random_avatar():
    return random.choice([902055006, 902050002, 902050003, 902039016, 902050004, 902047011, 902047010, 902049015, 902050006, 902049020])

def get_random_sticker():
    pack_id, start, end = random.choice([("1200000001", 1, 24), ("1200000004", 1, 15), ("1200000002", 1, 13)])
    return f"[1={pack_id}-{random.randint(start, end)}]"

def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))

async def encrypt_packet(packet_hex, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(packet_hex), AES.block_size)).hex()

# ═══════════════════════════════════════════════════════════════
# AUTH & DECODE
# ═══════════════════════════════════════════════════════════════
def build_ob55_online_auth(account_uid, token, kts, key, iv):
    token_bytes = token.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc_token = cipher.encrypt(pad(token_bytes, 16))
    opcode = bytes.fromhex("830c")
    uid_bytes = int(account_uid).to_bytes(8, byteorder="big")
    kts_bytes = int(kts).to_bytes(4, byteorder="big")
    len_bytes = len(enc_token).to_bytes(8, byteorder="big")
    return opcode + uid_bytes + kts_bytes + len_bytes + enc_token, enc_token

def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv) if isinstance(iv, str) else iv
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_token.encode('utf-8'), AES.block_size))
        return (bytes.fromhex('6d19') + int(account_id).to_bytes(8, 'big') + int(timestamp).to_bytes(4, 'big') + len(ct).to_bytes(4, 'big') + ct).hex()
    except: return None

async def cHTypE(H):
    return 'Squid' if not H else 'CLan' if H == 1 else 'PrivaTe'

async def DecodeWhisperMessage(hex_packet):
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(bytes.fromhex(hex_packet))
    return proto

async def get_colorful_message(message_text, message_number):
    color_palette = ["FFD700", "FFCC33", "DAA520", "FFE066", "F0C040", "FFB300", "E6BE00", "D4AF37", "CFB53B", "FFDF00", "F5C518", "E8B923"]
    return f"[C][B][{color_palette[(message_number - 1) % len(color_palette)]}]{message_text}"

# ═══════════════════════════════════════════════════════════════
# PACKET BUILDERS
# ═══════════════════════════════════════════════════════════════
async def NewClanChatPacket(message_text, key, iv, clan_id=3102281341):
    fields = {1: 16801068917, 2: 18, 4: 1, 5: {1: 16801068917, 2: clan_id, 3: 1, 4: 'DARK MASTER', 5: 1785944381, 7: 6, 9: {1: message_text, 4: 301, 8: 'DARK MASTER', 13: '', 14: {1: 16801068917}, 18: {1: 16801068917, 3: 1, 4: ''}}, 10: 'ar', 13: {2: 1, 3: 1}, 14: '', 16: int(time.time() * 1000)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid': return await xSEndMsgsQ(message, chat_id, key, iv)
    elif TypE == 'CLan': return await NewClanChatPacket(message, key, iv, chat_id)
    elif TypE == 'PrivaTe': return await xSEndMsg(message, 2, Uid, Uid, key, iv)

async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT: whisper_writer.write(PacKeT); await whisper_writer.drain()
    elif TypE == 'OnLine': online_writer.write(PacKeT); await online_writer.drain()

async def safe_send_message(chat_type, message, uid, chat_id, key, iv, max_retries=3):
    for attempt in range(max_retries):
        try:
            packet = await SEndMsG(chat_type, message, uid, chat_id, key, iv)
            if packet: await SEndPacKeT(whisper_writer, online_writer, 'ChaT', packet); return True
        except Exception: pass
        await asyncio.sleep(0.5)
    return False

async def JoinSq_original(code, K, V):
    skinz = {1: 4, 2: {4: "\u0001\u0007\t\n\u000b\u0012\u0019 '", 5: str(code), 6: 6, 8: 1,
        9: {1: "08FFF3BE903F27DF0203110111110000006B0003006800169194106F13CF106E4676251411010404dfe9e8b5ca3ca4f96a3119c00000004f03060301cacfa16d",
            2: 130, 3: "tY_S\u0013\b\u0001M\u0002\u0000T\u0000\u0005\u000e\b\t\u0002\u0000\u0003U\u0003\u0001V\u000fR\u000e\tRQ\u0002\u0004\u0005US\u0003XS\u0005\u0001\u0002\u0011\u0001\u0002JuTAEN\u001e\u0002\u001c\u0002\u001f\u0013\b\u0003M\u001cDbz_Q@}p_QOgsC\u001dYVI\u0004UAAj_ga\u0004\u0012\u0000K\u001d\u0007_t\u0019b\bCx\u0002UeGat\u001fTTCBLER`\u0006\u0001\r\f\u0012\u0006\u0005N^^\u0002acH~r\u0004_\u0003RO|\u000bcd_@~`Rnqrgh\n\u0015\nL\\Nh\u0000~G\u000et\u0000eb]VQ\u0006t^F[ZIGxCdZD\u000b\u0011\u0002OA~LP@\u000fcSDyATQApaT^{|wa]\\\u0001E\u000f\u0013\nJfxve}\u0004J\u0003c{YL\u0007^^yDYQf\bhe\u0005_wg\r\u0010\u0007\bEHpX@||\u0002Z\\uTGyA\u0001JP\u0005t~VkTE\u0000J\\\u000b\u0013\nMr\u0018zTzK}qE]vnvwROuheYvwduvQ\r\u001a\u0005M\u0006z\u001dfXfzvHFc~dXUz}O\u001aB\u0005t\u0002i\u001co_\u0004\u0012\u0003\u0007J\u0006b\u0003\u000eqlfvbEstgu~wB\u0001v@`yI\u0002ZPx\f\u0014\u0003NR\u0002yBZvuD_cd\u0004q]lH]\u0007bD}pCe\t\u0004t\n",
            4: "w^_R", 6: 11, 7: "\u0014\u0004aqrg\u0015\u0013", 8: "1.132.1", 9: 3, 10: 2,
            11: "\u0003bbSQ6wxegh9qAdV2KyoVleA17yPmYF+yTnOrl+JMknmppeUBe5ZsiHueP2mZZ4KOs6b2Ail1S9z3qIeU9hGFZ2M6PP39/zjIc/RFVPAkgDagySswMVmYaPhkzU5IqNPow2843fyQUz9xI10NdMhl1WiI4Y6wCXBotiUS9wSgujQ4j0fWXUyklCxBWo8r27hyoGSVrPdTPXFMnJJpPRRFFmWqc3fWvMg+BNfxSRJOZRSrkzG0nNvSIJ4uZB2pqAlHIPEYx7bI6zsgwUVDiLZJKTUTyuCGbOd1DegDUFfazFesTG1LJknT5WhgzCsrBIy+f2l+LeJe5DW7wEwNaHambM7ECXcJcLIhB9kJJsW0tFvXkk3HSdcQ8N1K6wjSKWhpkW0kV8Zrjj0jkhS/7AZ6T9GJRIA827YDtTorBvbx1UkXjYrqYI1nSa2GaMexGnqlurc5DE3v1R+mUBI9GqmjEPgTSYVBxyeCdQMHaMXGtspAhvkiO84ToU87sP45pylDEfFOVoc/rcmdzWeqlYPsv6txKRtIHcb0cO+MoVShoU8ZUVRDF3znbqzVrscPIfplBaa79lwvQqzRubLl9XY="},
        11: {1: "IDC4", 2: 281, 3: "ME"}, 13: "fr", 16: "7OR\u0019", 20: "\b\u0015", 27: "\bH\u0010\u0003"}}
    return await GeneRaTePk((await CrEaTe_ProTo(skinz)).hex(), '0515', K, V)

async def MahirAccepted(uid, code, K, V, region):
    fields = {1: 4, 2: {1: int(uid), 3: int(uid), 4: "rYUW\u0017\t\u0007NR\u000f\u0005\u0004\\W\u0002\u000fV\u0004TPQ\u0003\u000f\u0005\u0004]\u0005\u000b\u0000\u0002W\u0005\r\nVY\u0004\u0007\u0007\u0007\u0017\u0001\bNQ\fS\u0005\u000e\u0006\f\u0005\rT\u0002\r\u0000TS\u0007U\u0004X\u0006RY\u0005\u0003\u0003SW\u0000\u000eQ\u0000^\u0014\u0003\u0004JXS\u000f\u0000g{gqfePblEZJp{_xU\bmQW\f\u0007\u000f\u0015\u0007H\\U^CHXh@Ax`\u000f~\rPN~Nz\\\u001fr_ckPU\u000b\u0015\u0005\u0003Ekfp\u007fcY\u0001nWV\u0002\u0005azE~N\u0007HTg\u0007w}@\u0002{\t\u0013\u0001NeNP]DUf|]ugINs{\u0001\\rAgB_\u0004fA]\u0004\r\u001a\u0000HpOv\\\u0005|gS\u0019\\A\u007fWW\u0003\u007fTqFGi\u0004Qr\u0019dW\u0004\u0011\rD\u0002yeZ]A\u0016a\u0007Ungeg\u0007E\\P\u001b\u000b\u0004\u0005dd\ff\r\u000f\u0017\t\u000fNRyZd\u0012tZ\fe\u0007AGv\u007fw]{P\u001c\u007ff\u0005ZJK\u0004\u0005\u0014\u0001Jgq\u001frymsB\u0001\u000fd`\u001bj~[}\u0004SDZ|IxKB\u0000\n\u0011\u0002J^`tjYN\u0007WQdE[PQ\u0002_{VP`S\t\u007f\u001dP\n\u000f\u000f\u0015\u0004\u0004L{V\u0003@yP[rgJ{Hpk\u0001\u000bw\u0001Agt_\u0003HxPc\u000b\u0017\u0005E`y\ngWoy\u0006S{A\u001b``Y\u0002Xzw}dDWOKsg\t\u0013\u000eNf\u000e\\`\u0005AwJc\u0003BM\u0001^\u0000R\u0002Qoh]tbS~`G\r\u001a\u0004HibAQ\u000f^XNt~kDUWaeaNqcLQ]Py[G\u0004",
            8: 1, 9: {1: "08FBA33CFF105FDD02030A01111100000003000100020000B687046B0D6D2083467625141101030175a63c900e748c3f6a311e04000000ff00040202cacfa16d",
            2: 197, 3: "735154531406054a035305025a0e50560f5100040250020f5e0401520653000303505e0d520302501500064d705548424e1f051a001e12040a441d45677f5a56477574565e4f6274451d585849005a4f456d5b64670c1400496d017842740c670100040069536e72586c02016e657e566b524403081500044d0d515b637f757c19095c7c510b00417f565e5e066f5b584d6e02400a160e4d58496d0177400e750763605c575d0f7d5f475e5f4c407f4b60534b0b140549751e66407a4860726e44400e6103557e515c646f43577106077b60051b0f4b4e474e58457e4f615c01406000051e0361516e7b67614e040102540c1609004a0e40730f62517f446a135179507e706850547f7e7a67795553597c0a1206445b456640046265725c4d505d446d50737b7c42035970486370645e0b12034d506f5c7a1c554f574b0e765a0f0a7364505203477569456c6c420f0a1604014b647149136c186f795f5d78755e550e7842545e53747b08705f7f5d0a14004a08666b5a5b5f00045c7f5e584d72584262705f56055c61475564790515004b76514178587f52797a0f077a070953507d7f4d784f794f667b4256081b0e4a75627d4778417a06717574747c4c78557b4b7a0a697f0e714573600a",
            4: "{Y_R", 6: 13, 7: "1c6f017306741513", 8: "2.126.22", 9: 2, 10: 1,
            11: "036262535136784d584e38742b416456324b796f566c6537392f763672324d4773683377706379634f6b6b6f7447397934523930517432797246474c464c624c777a7747344d4d5257623146756d2b6556777a62597736743973492b787059612f55596e43465a59485235713348705830306c485a6f3632565145574e7145705866414c38734a754646575247386d376f5444566a4c484c576e714c52576f4e653236437a734c346a4144482b71694b55384d71476c5936546669544863716c487a345568463869396a365233366d49774b71746c36714f797568513854367945714b69742f45466d2b3636634b787649304f384d6c41385166454b6253467366477a2f30684e6a543873305369722f3962635a2f4679376c752f61632f366765704d415734566b442b36374f535756473665377a775a79312b797a42334b70632b7571782b577437414d39727761644439575765704570567849526d66654f5847627775787a68574b5664344c49586f415a364b387063647450627953575857455135706a542b653669365a2f6177444a3179356f774d5a534f64487262392b7877424a4d444f7848565a7a483372547a30314a316738517675466b656c3042433746473630683456427041494457487956684e794b4f5145507139467a4a6272686b316146306768766578512f6a2f484767426a5268675134645243372b477a5a687a2b77505967376454746f2b494d56363774642b54435653314234346b4148395a6d415872763758615941626477644e664f533170484875736b7336346f72463452534d3772656345417661484e61484854314c5545686e786a5a616d4d4f303d"},
            10: str(code), 11: {1: "IDC3", 2: 84, 3: "BD"}, 13: "en", 16: "374f5219",
            20: {1: 21}, 23: "a_1477547277882450725", 27: {1: 2, 2: 8}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def leave_channel_req(channel_id, channel_type, key, iv):
    fields = {1: 4, 2: {1: int(channel_id), 2: int(channel_type), 3: "en"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', key, iv)

async def SPamSqForSpm(Uid, K, V):
    same_value = random.choice([4096, 16384, 8192])
    fields = {1: 33, 2: {1: int(Uid), 2: "ME", 3: 1, 4: 1,
        5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]), 6: "iG:[C][B][FFD700] DARK MASTER",
        7: 330, 8: 1000, 10: "ME",
        11: bytes([49,97,99,52,98,56,48,101,99,102,48,52,55,56,97,52,52,50,48,51,98,102,56,102,97,99,54,49,50,48,102,53]),
        12: 1, 13: int(Uid),
        14: {1: 2203434355, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
        16: 1, 17: 1, 18: 312, 19: 46, 23: bytes([16, 1, 24, 1]),
        24: await xBunnEr(), 26: "", 28: "",
        31: {1: 1, 2: same_value}, 32: same_value,
        34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}},
        10: "en", 13: {2: 1, 3: 1}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def GhostPakcet(player_id, nm, secret_code, key, iv):
    fields = {1: 61, 2: {1: int(player_id), 2: {1: int(player_id), 2: 1159,
        3: f"[b][c]{get_random_color()}{nm}", 5: 12, 6: 999, 7: 1,
        8: {2: 1, 3: 1}, 9: 3}, 3: secret_code}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

async def xBaNchaTxSkInZ(uidd, K, V):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 3, 2: {1: int(uidd), 3: "fr", 4: "1750728024661459697_3qind8eeqs"}})).hex(), '1215', K, V)

async def send_sticker_packet(target_uid, chat_id, key, iv, nickname="DARK MASTER"):
    try:
        sticker_value = get_random_sticker()
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()), 8: f'{{"StickerStr" : "{sticker_value}", "type":"Sticker"}}',
            9: {1: f"[C][B][FFD700]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                8: "DARK MASTER", 10: 1, 11: 66, 12: 66, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Sticker error: {e}")
        return None

async def animation_packet(animation_id, key, iv):
    fields = {1: 88, 2: {1: {1: int(animation_id)}}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    pl = len(encrypted) // 2
    hl = format(pl, 'x')
    final = "051500" + "0" * (6 - len(hl)) + hl + encrypted
    return bytes.fromhex(final)

async def Look_Changer(bundle_id, key, iv, look_type=1, region="bd"):
    fields = {1: 88, 2: {1: {1: bundle_id, 2: look_type}, 2: 2}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if region.lower() == "ind": pt = "0514"
    elif region.lower() == "bd": pt = "0519"
    else: pt = "0515"
    if len(hl) == 2: h = f"{pt}000000"
    elif len(hl) == 3: h = f"{pt}00000"
    elif len(hl) == 4: h = f"{pt}0000"
    elif len(hl) == 5: h = f"{pt}000"
    else: h = f"{pt}000000"
    return bytes.fromhex(h + hl + encrypted)

async def Room_Spam(Uid, Rm, Nm, K, V):
    fields = {1: 78, 2: {1: int(Rm), 2: "iG:[C][B][FFD700]DARK MASTER", 3: {2: 1, 3: 1},
        4: 330, 5: 6000, 6: 201, 10: get_random_avatar(), 11: int(Uid), 12: 1,
        15: {1: 1, 2: 32768}, 16: 32768,
        18: {1: 11481904755, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
        31: {1: 1, 2: 32768}, 32: 32768,
        34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0e15', K, V)

async def banecipher(target_uid, key, iv):
    banner_text = ".\n.\n.\n[b][FFD700]DARK MASTER[FFEA70] ⚡\n.\n.\n."
    fields = {1: 5, 2: {1: int(target_uid), 2: 1, 3: int(target_uid), 4: banner_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2: f = "0515000000"
    elif len(hl) == 3: f = "051500000"
    elif len(hl) == 4: f = "05150000"
    elif len(hl) == 5: f = "0515000"
    else: f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)

async def banecipher1(target_uid, key, iv):
    gay_text = ".\n.\n.\n[b][FFD700]DARK MASTER ⚡[FFEA70]\n.\n.\n."
    fields = {1: int(target_uid), 2: 5, 4: 50, 5: {1: int(target_uid), 2: gay_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2: f = "0515000000"
    elif len(hl) == 3: f = "051500000"
    elif len(hl) == 4: f = "05150000"
    elif len(hl) == 5: f = "0515000"
    else: f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)

async def convert_kyro_to_your_system(target_uid, chat_id, key, iv, nickname="DARK MASTER", title_id=None):
    try:
        if title_id is None:
            available_titles = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015, 904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
            title_id = random.choice(available_titles)
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()),
            8: f'{{"TitleID":{title_id},"type":"Title"}}',
            9: {1: f"[C][B][FFD700]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007, 8: "DARK MASTER", 10: 1, 11: 1, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Title error: {e}")
        return None

async def xSEndMsgsQQ(Msg, id, K, V):
    fields = {1: id, 2: id, 4: Msg, 5: 1756580149, 7: 2, 8: 904990072,
        9: {1: "DARK MASTER", 2: get_random_avatar(), 4: 330, 5: 1001000001, 8: "DARK MASTER", 10: 1, 11: 1, 13: {1: 2},
            14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}},
        10: "en", 13: {2: 2, 3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)

# ═══════════════════════════════════════════════════════════════
# LOOPS
# ═══════════════════════════════════════════════════════════════
async def spm_loop(uid, key, iv, interval=0.5):
    while True:
        try:
            if online_writer is not None:
                packet = await SPamSqForSpm(uid, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', packet)
            else: await asyncio.sleep(1)
        except asyncio.CancelledError: break
        except Exception: pass
        await asyncio.sleep(interval)

async def ban_loop(key, iv, interval=0.5):
    global ban_running, ban_targets
    ban_running = True
    while ban_running:
        if online_writer is not None and ban_targets:
            for uid in list(ban_targets):
                try:
                    ban_pkt = await xBaNchaTxSkInZ(uid, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ban_pkt)
                except Exception: pass
        await asyncio.sleep(interval)

async def evo_gun_cycle(uids, evo_ids_list, key, iv, region):
    global evo_cycle_running
    cc = 0
    while evo_cycle_running:
        cc += 1
        for emote_id in evo_ids_list:
            if not evo_cycle_running: break
            for uid_str in uids:
                try:
                    H = await Emote_k(int(uid_str), int(emote_id), key, iv, region)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                except Exception: pass
            if evo_cycle_running:
                for i in range(5):
                    if not evo_cycle_running: break
                    await asyncio.sleep(1)
        if evo_cycle_running: await asyncio.sleep(2)

async def fast_emote_spam(uids, emote_id, key, iv, region):
    global fast_spam_running
    count = 0
    while fast_spam_running and count < 25:
        for uid in uids:
            try:
                H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception: pass
        count += 1
        await asyncio.sleep(0.1)

async def custom_emote_spam(uid, emote_id, times, key, iv, region):
    global custom_spam_running
    count = 0
    while custom_spam_running and count < times:
        try:
            H = await Emote_k(int(uid), int(emote_id), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            count += 1
            await asyncio.sleep(0.1)
        except Exception: break

async def reject_spam_loop(target_uid, key, iv):
    global reject_spam_running
    count = 0
    while reject_spam_running and count < 150:
        try:
            p1 = await banecipher1(target_uid, key, iv)
            p2 = await banecipher(target_uid, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p1)
            await asyncio.sleep(0.1)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p2)
            count += 1
            await asyncio.sleep(0.2)
        except Exception: break
    return count

async def msg_spam_loop(message_text, times, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    while msg_spam_running and count < times:
        try:
            colorful = await get_colorful_message(message_text, count + 1)
            msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
            if msg_packet and whisper_writer:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                count += 1
                await asyncio.sleep(0.1)
        except Exception: break
    return count

async def send_wave_messages(message_text, repeats, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    total_cycles = 0
    while msg_spam_running and total_cycles < repeats:
        try:
            for i in range(1, len(message_text) + 1):
                if not msg_spam_running: break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            for i in range(len(message_text) - 1, 0, -1):
                if not msg_spam_running: break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            total_cycles += 1
        except Exception: break
    return count, total_cycles

async def freeze_emote_spam(uid, key, iv, region, chat_type, chat_id, sender_uid):
    global freeze_running
    FREEZE_EMOTES = [909052010, 909052010, 909052010]
    cycles = 0
    while freeze_running and cycles < 10:
        for emote_id in FREEZE_EMOTES:
            if not freeze_running: break
            try:
                emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
                await asyncio.sleep(0.1)
            except Exception: pass
        cycles += 1
        await asyncio.sleep(1)
    return cycles

# ═══════════════════════════════════════════════════════════════
# API CALLS
# ═══════════════════════════════════════════════════════════════
async def send_friend_request(target_uid, token, region):
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        ep = cipher.encrypt(pad(bytes.fromhex(payload), AES.block_size)).hex()
        url = "https://clientbp.ggpolarbear.com/RequestAddingFriend"
        headers = {"Authorization": f"Bearer {token}", "X-Unity-Version": "2018.4.11f1", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=bytes.fromhex(ep), ssl=False) as r:
                return (True, "✅ Friend request sent") if r.status == 200 else (False, f"❌ Status: {r.status}")
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

async def remove_friend(target_uid, token, region):
    try:
        import RemoveFriend_Req_pb2
        msg = RemoveFriend_Req_pb2.RemoveFriend()
        msg.AuthorUid = int(admin_uid); msg.TargetUid = int(target_uid)
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        eb = cipher.encrypt(pad(msg.SerializeToString(), AES.block_size))
        url = "https://clientbp.ggpolarbear.com/RemoveFriend"
        headers = {'Authorization': f"Bearer {token}", 'User-Agent': "Dalvik/2.1.0 (Linux; Android 9)", 'Content-Type': "application/x-www-form-urlencoded", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB55"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=eb, headers=headers, ssl=False) as r:
                return (True, "✅ Friend removed") if r.status == 200 else (False, f"❌ Status: {r.status}")
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

async def check_banned(player_id):
    try:
        url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Accept": "application/json", "referer": "https://ff.garena.com/en/support/", "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as r:
                if r.status == 200: return True, await r.json()
                return False, f"Failed: {r.status}"
    except Exception as e: return False, f"Error: {str(e)}"

async def get_player_info(player_id):
    try:
        url = f"https://smt-info-api.vercel.app/info?uid={player_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200: return True, await r.json()
                return False, f"HTTP {r.status}"
    except Exception as e: return False, str(e)

def format_player_info(data):
    if data.get("status") != "success":
        return [f"[B][C][FF0000]❌ API Error: {data.get('message', 'Unknown')}"]
    b = data.get("BasicInformation", {})
    a = data.get("ActivityInformation", {})
    g = data.get("GuildInformation", {})
    l = data.get("LeaderInformation", {})
    p = data.get("PetDetails", {})
    ban = data.get("BanStatus", "Unknown")

    p1 = f"""[B][C][FFD700]╔══════════════════╗
[B][C][FFD700]║   DARK MASTER INFO   ║
[B][C][FFD700]╚══════════════════╝
[B][C][DAA520]┌─[ 1/3 ]──────────────
[B][C][FFFFFF]👤 Name: [FFD700]{b.get('Name', 'N/A')}
[B][C][FFFFFF]🆔 UID: [FFEA70]{b.get('UID', 'N/A')}
[B][C][FFFFFF]🌍 Region: [DAA520]{b.get('Region', 'N/A')}
[B][C][FFFFFF]📊 Level: [FFCC33]{b.get('Level', 'N/A')}
[B][C][FFFFFF]❤️ Likes: [FFD700]{b.get('Likes', 'N/A')}
[B][C][FFFFFF]⚔️ BR Rank: [E6BE00]{a.get('BRRank', 'N/A')} ({a.get('BRPoints', 0)} pts)
[B][C][FFFFFF]🛡️ Ban: {ban}
[B][C][FFFFFF]📝 Bio: [F0C040]{b.get('Signature', 'N/A')}
[B][C][DAA520]└────────────────────"""

    p2 = f"""[B][C][FFD700]╔══════════════════╗
[B][C][FFD700]║  GUILD & LEADER  ║
[B][C][FFD700]╚══════════════════╝
[B][C][DAA520]┌─[ 2/3 ]──────────────
[B][C][FFFFFF]🏰 Guild: [FFD700]{g.get('GuildName', 'No Guild')}
[B][C][FFFFFF]🆔 Guild ID: [FFEA70]{g.get('GuildID', '0')}
[B][C][FFFFFF]📈 Guild Lv: [FFCC33]{g.get('GuildLevel', '0')}
[B][C][FFFFFF]👥 Members: [DAA520]{g.get('LiveMembers', 0)}/{g.get('MaxMembers', 0)}
[B][C][FFFFFF]─────────────────────
[B][C][FFFFFF]👑 Leader: [FFD700]{l.get('Name', 'N/A')}
[B][C][FFFFFF]🆔 Leader UID: [FFEA70]{l.get('UID', 'N/A')}
[B][C][FFFFFF]📊 Leader Lv: [FFCC33]{l.get('Level', 'N/A')}
[B][C][FFFFFF]⚔️ Leader BR: [E6BE00]{l.get('BRRank', 'N/A')}
[B][C][DAA520]└────────────────────"""

    p3 = f"""[B][C][FFD700]╔══════════════════╗
[B][C][FFD700]║  ACTIVITY & EXTRA  ║
[B][C][FFD700]╚══════════════════╝
[B][C][DAA520]┌─[ 3/3 ]──────────────
[B][C][FFFFFF]🐾 Pet: [FFD700]{p.get('PetNick', 'N/A')} (Lv {p.get('PetLevel', 0)})
[B][C][FFFFFF]🌟 Celebrity: [FFEA70]{b.get('CelebrityStatus', 'No')}
[B][C][FFFFFF]🏅 Honor: [FFCC33]{b.get('HonorScore', 0)}
[B][C][FFFFFF]📅 Created: [DAA520]{a.get('CreatedAt', 'N/A')}
[B][C][FFFFFF]⏰ Last Login: [F0C040]{a.get('LastLogin', 'N/A')}
[B][C][FFFFFF]🎖️ BP Badges: [E6BE00]{a.get('CurrentBpBadges', 0)}
[B][C][FFFFFF]🆕 Recent OB: [FFD700]{a.get('MostRecentOB', 'N/A')}
[B][C][DAA520]└────────────────────
[B][C][FFD700]✨ DARK MASTER ✨"""
    return [p1, p2, p3]

def format_check_result(data):
    try: return f"[b][c][FFD700] 🔍 BAN CHECK\n[b][c][FFFFFF]Type: [FFEA70]{data.get('ban_type', 'Unknown')}\n[b][c][FFFFFF]Duration: [FFCC33]{data.get('ban_duration', 'Unknown')}\n[b][c][DAA520]— DARK MASTER —"
    except Exception as e: return f"[b][c]Error: {str(e)}"

# ═══════════════════════════════════════════════════════════════
# HELP MENU — নতুন প্রিমিয়াম গোল্ডেন ডিজাইন
# ═══════════════════════════════════════════════════════════════
def get_emote_menu():
    named_list = " • ".join(NAME_EMOTES.keys())
    try:
        emote_numbers = sorted(EMOTE_MAP.keys())
        num_list = ", ".join(str(n) for n in emote_numbers)
    except Exception:
        num_list = "1-21"
    try:
        single_numbers = sorted(SINGLE_EMOTES_MAP.keys(), key=lambda x: int(x))
        single_list = ", ".join(single_numbers)
    except Exception:
        single_list = "N/A"

    return f"""[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFD700]      🎭  E M O T E   M E N U
[B][C][FFD700]✦ ─────────────────── ✦

[B][C][DAA520]▸ [FFEA70]/e <uid> <num>  [FFFFFF]→ Single emote
[B][C][DAA520]▸ [FFEA70]/e <name>       [FFFFFF]→ Named emote
[B][C][DAA520]▸ [FFEA70]/evo <uid> <1-21> [FFFFFF]→ Evo emote
[B][C][DAA520]▸ [FFEA70]/evos           [FFFFFF]→ Start evo cycle
[B][C][DAA520]▸ [FFEA70]/sevos          [FFFFFF]→ Stop evo cycle
[B][C][DAA520]▸ [FFEA70]/sticker        [FFFFFF]→ Random sticker

[B][C][FFD700]✦ ───── NAMED ───── ✦
[B][C][FFEA70]{named_list}

[B][C][FFD700]✦ ─── EVO (1-21) ─── ✦
[B][C][FFCC33]{num_list}

[B][C][FFD700]✦ ── SINGLE ── ✦
[B][C][E6BE00]{single_list}

[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFEA70]      ✨ DARK MASTER ✨"""

def get_squad_menu():
    return f"""[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFD700]      🎮  S Q U A D   M E N U
[B][C][FFD700]✦ ─────────────────── ✦

[B][C][DAA520]▸ [FFEA70]/5             [FFFFFF]→ 5-man team
[B][C][DAA520]▸ [FFEA70]/6             [FFFFFF]→ 6-man team
[B][C][DAA520]▸ [FFEA70]/3             [FFFFFF]→ 3-man team
[B][C][DAA520]▸ [FFEA70]/4             [FFFFFF]→ 4-man team
[B][C][DAA520]▸ [FFEA70]/join <code>   [FFFFFF]→ Join squad
[B][C][DAA520]▸ [FFEA70]/exit          [FFFFFF]→ Leave squad

[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFEA70]      ✨ DARK MASTER ✨"""

def get_attack_menu():
    return f"""[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFD700]      💥  A T T A C K   M E N U
[B][C][FFD700]✦ ─────────────────── ✦

[B][C][DAA520]▸ [FFEA70]/spm <uid>      [FFFFFF]→ Spam requests
[B][C][DAA520]▸ [FFEA70]/stp <uid>      [FFFFFF]→ Stop spam
[B][C][DAA520]▸ [FFEA70]/msg <text> <n> [FFFFFF]→ Msg spam
[B][C][DAA520]▸ [FFEA70]/mg <text> [n]  [FFFFFF]→ Wave msg
[B][C][DAA520]▸ [FFEA70]/ban <uid>      [FFFFFF]→ Ban loop
[B][C][DAA520]▸ [FFEA70]/reject <uid>   [FFFFFF]→ Reject spam
[B][C][DAA520]▸ [FFEA70]/reject_stop    [FFFFFF]→ Stop reject
[B][C][DAA520]▸ [FFEA70]/fast <uid> <n> [FFFFFF]→ Fast emote
[B][C][DAA520]▸ [FFEA70]/p <uid> <e> <n>[FFFFFF]→ Custom spam

[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFEA70]      ✨ DARK MASTER ✨"""

def get_bundle_menu():
    return f"""[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFD700]      🎁  B U N D L E   M E N U
[B][C][FFD700]✦ ─────────────────── ✦

[B][C][DAA520]▸ [FFEA70]/b <1-12>        [FFFFFF]→ Send bundle
[B][C][DAA520]▸ [FFEA70]/animation <1-12> [FFFFFF]→ Animation
[B][C][DAA520]▸ [FFEA70]/title          [FFFFFF]→ Send title
[B][C][DAA520]▸ [FFEA70]/alltitles      [FFFFFF]→ All titles

[B][C][FFD700]✦ ─── BUNDLE LIST ─── ✦
[B][C][FFEA70]1-rampage     2-cannibal
[B][C][FFEA70]3-devil       4-scorpio
[B][C][FFEA70]5-frostfire   6-paradox
[B][C][FFEA70]7-naruto      8-aurora
[B][C][FFEA70]9-midnight    10-itachi
[B][C][FFEA70]11-dreamspace 12-eclipse

[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFEA70]      ✨ DARK MASTER ✨"""

def get_info_menu():
    return f"""[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFD700]      🔍  I N F O   M E N U
[B][C][FFD700]✦ ─────────────────── ✦

[B][C][DAA520]▸ [FFEA70]/info <uid>     [FFFFFF]→ Player Info
[B][C][DAA520]▸ [FFEA70]/check <uid>    [FFFFFF]→ Ban Check
[B][C][DAA520]▸ [FFEA70]/mth <expr>     [FFFFFF]→ Calculator

[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFEA70]      ✨ DARK MASTER ✨"""

def get_admin_menu():
    return f"""[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFD700]      🎭  E M O T E   M E N U
[B][C][FFD700]✦ ─────────────────── ✦

[B][C][DAA520]▸ [FFEA70]/e <uid> <num>  [FFFFFF]→ Single emote
[B][C][DAA520]▸ [FFEA70]/e <name>       [FFFFFF]→ Named emote
[B][C][DAA520]▸ [FFEA70]/evo <uid> <1-21> [FFFFFF]→ Evo emote
[B][C][DAA520]▸ [FFEA70]/evos           [FFFFFF]→ Start evo cycle
[B][C][DAA520]▸ [FFEA70]/sevos          [FFFFFF]→ Stop evo cycle
[B][C][DAA520]▸ [FFEA70]/sticker        [FFFFFF]→ Random sticker

[B][C][FFD700]✦ ─────────────────── ✦
[B][C][FFEA70]      ✨ DARK MASTER ✨"""

def get_all_help_pages():
    """সিরিয়ালি সব মেনু — একবার আসবে, তারপর থামবে"""
    return [
        get_emote_menu(),
        get_squad_menu(),
        get_attack_menu(),
        get_bundle_menu(),
        get_info_menu(),
        get_admin_menu(),
    ]

# ═══════════════════════════════════════════════════════════════
# TCP ONLINE HANDLER
# ═══════════════════════════════════════════════════════════════
async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, whisper_writer, region, pending_ghost_future, ghost_team_id, ghost_squad_code, emote_hijack, bot_uid
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            token_bytes = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            writer.write(token_bytes); await writer.drain()
            print(f"✅ ONLINE connected to {ip}:{port}")
            while True:
                data = await reader.read(9999)
                if not data: break
                hex_data = data.hex()
                if not hex_data.startswith("0500"): continue
                try: packet_json = json.loads(await DeCode_PackEt(hex_data[10:]))
                except Exception: continue
                try:
                    if ('5' in packet_json and 'data' in packet_json['5'] and '1' in packet_json['5']['data'] and '8' in packet_json['5']['data']):
                        owner = packet_json['5']['data']['1']['data']
                        code = packet_json['5']['data']['8']['data']
                        join_pkt = await MahirAccepted(owner, code, key, iv, region)
                        if join_pkt and online_writer: await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_pkt)
                except Exception: pass
                try:
                    uid_g = packet_json['5']['data']['1']['data']
                    chat_code = packet_json['5']['data']['17']['data']
                    squad_code = packet_json['5']['data']['31']['data']
                    if uid_g is not None:
                        INV_JOIN = await AutH_Chat(3, uid_g, chat_code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', INV_JOIN)
                except Exception: pass
                try:
                    if pending_ghost_future and not pending_ghost_future.done():
                        f5 = packet_json.get('5', {}).get('data', {})
                        if '31' in f5: ghost_squad_code = f5['31'].get('data')
                        if '1' in f5: ghost_team_id = f5['1'].get('data')
                        if ghost_team_id and ghost_squad_code: pending_ghost_future.set_result(True)
                except Exception: pass
                try:
                    if packet_json.get('4', {}).get('data') == 8:
                        f5 = packet_json.get('5', {}).get('data', {})
                        if f5.get('2', {}).get('data') == 5:
                            chat_code = f5.get('17', {}).get('data')
                            if chat_code is not None:
                                LeAvE = await leave_channel_req(chat_code, 3, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', LeAvE)
                except Exception: pass
            writer.close(); await writer.wait_closed(); online_writer = None
        except Exception as e:
            print(f"Online error: {ip}:{port} - {e}")
            online_writer = None
        await asyncio.sleep(reconnect_delay)

# ═══════════════════════════════════════════════════════════════
# TCP CHAT HANDLER
# ═══════════════════════════════════════════════════════════════
async def TcPChaT(ip, port, AutHToKen, key, iv, ready_event, region, reconnect_delay=0.5):
    global whisper_writer, online_writer, spm_tasks, ToKen, bot_uid, bot_enabled, emote_hijack
    global spam_targets, evo_cycle_running, evo_cycle_task, ban_task, ban_running, ban_targets
    global fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task
    global msg_spam_running, msg_spam_task, mg_spam_task
    global reject_spam_running, reject_spam_task, freeze_running, freeze_task

    print(f"📡 {region} → TCP CHAT connecting...")
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            whisper_writer.write(bytes_payload); await whisper_writer.drain()
            ready_event.set()
            print(f"✅ CHAT connected to {ip}:{port}")

            for tgt in spam_targets:
                if tgt not in spm_tasks or spm_tasks[tgt].done():
                    spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))

            while True:
                data = await reader.read(9999)
                if not data: break
                if not data.hex().startswith("120000"): continue
                try:
                    response = await DecodeWhisperMessage(data.hex()[10:])
                    uid = response.Data.uid
                    chat_id = response.Data.Chat_ID
                    XX = response.Data.chat_type
                    inPuTMsG = response.Data.msg.lower()
                except Exception: continue

                command_text = inPuTMsG.strip()
                command = command_text.split()[0].split("@")[0].lower() if command_text else ""

                if not bot_enabled and command not in ("/on", "/admin", "/help", "help"): continue

                # ═══ /help — একবারে সব মেনু সিরিয়ালি, তারপর থেমে যাবে ═══
                if command_text.startswith("/help") or command_text in ("help",):
                    pages = get_all_help_pages()
                    for page_text in pages:
                        try:
                            await safe_send_message(XX, page_text, uid, chat_id, key, iv)
                        except Exception as e:
                            print(f"Help err: {e}")
                        await asyncio.sleep(3.5)
                    # সব মেনু পাঠানো শেষ — আর কিছু পাঠাবে না

                # ═══ /admin ═══
                elif command in ("/admin", "admin"):
                    msg = f"""[b][c][FFD700]╔══════════════════════════╗
[b][c][FFD700]║   ⚡ DARK MASTER ⚡       ║
[b][c][FFD700]╚══════════════════════════╝
[b][c][DAA520]┌──[ 👑 OWNER INFO ]───────
[b][c][FFFFFF]👤 Name: [FFD700]DARK MASTER
[b][c][FFFFFF]👑 Dev : [FFEA70]DARK MASTER
[b][c][FFFFFF]✈ TG  : [DAA520]https://t.me/dark_master
[b][c][FFFFFF]🎮 Free Fire Mini SRC Developer
[b][c][FFFFFF]⚡ DARK MASTER TCP BOT
[b][c][DAA520]└──────────────────────
[b][c][FFD700]✨ Powered by DARK MASTER"""
                    await safe_send_message(XX, msg, uid, chat_id, key, iv)

                # ═══ /on /off ═══
                elif inPuTMsG.strip() == '/on':
                    if str(uid) != admin_uid: await safe_send_message(XX, f"[B][C][FF0000]❌ Only admin can use /on", uid, chat_id, key, iv)
                    else: bot_enabled = True; await safe_send_message(XX, f"[B][C][00FF00]✅ Bot is now ON", uid, chat_id, key, iv)
                elif inPuTMsG.strip() == '/off':
                    if str(uid) != admin_uid: await safe_send_message(XX, f"[B][C][FF0000]❌ Only admin can use /off", uid, chat_id, key, iv)
                    else: bot_enabled = False; await safe_send_message(XX, f"[B][C][FF0000]⛔ Bot is now OFF", uid, chat_id, key, iv)

                # ═══ /evos /sevos ═══
                elif inPuTMsG.startswith('/evos'):
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False; evo_cycle_task.cancel(); await asyncio.sleep(0.3)
                    evo_cycle_running = True
                    evo_cycle_task = asyncio.create_task(evo_gun_cycle([str(uid)], EVO_IDS, key, iv, region))
                    await safe_send_message(XX, f"[B][C][FFD700]✅ Evo cycle started", uid, chat_id, key, iv)
                elif inPuTMsG.strip() == '/sevos':
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False; evo_cycle_task.cancel()
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Evo cycle stopped", uid, chat_id, key, iv)

                # ═══ /e ═══
                elif inPuTMsG.startswith('/e '):
                    parts = inPuTMsG.strip().split()
                    try:
                        if len(parts) < 2: continue
                        last = parts[-1].lower()
                        is_num = last.isdigit() and last in SINGLE_EMOTES_MAP
                        is_name = last in NAME_EMOTES
                        if not (is_num or is_name):
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Emote '{last}' not found", uid, chat_id, key, iv)
                            continue
                        tgt_uids = []
                        if len(parts) == 2: tgt_uids.append(int(uid))
                        else:
                            for p in parts[1:-1]:
                                if p.isdigit(): tgt_uids.append(int(p))
                        emote_id = SINGLE_EMOTES_MAP.get(last) if is_num else NAME_EMOTES.get(last)
                        sc = 0
                        for t in tgt_uids:
                            try:
                                H = await Emote_k(t, int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                sc += 1
                                await asyncio.sleep(0.1)
                            except Exception: pass
                        if sc > 0:
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Emote sent to {sc} player(s)", uid, chat_id, key, iv)
                    except Exception as e: print(f"E cmd error: {e}")

                # ═══ /evo ═══
                elif inPuTMsG.startswith('/evo ') and not inPuTMsG.startswith('/evos'):
                    parts = inPuTMsG.strip().split()
                    try:
                        num = None; uids_l = []
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) <= 2 and num is None: num = p
                                else: uids_l.append(p)
                        if not num or not uids_l:
                            await safe_send_message(XX, f"[B][C][FF0000]Usage: /evo <uid> <1-21>", uid, chat_id, key, iv)
                            continue
                        num_i = int(num)
                        if num_i not in EMOTE_MAP:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Number must be 1-21", uid, chat_id, key, iv)
                            continue
                        emote_id = EMOTE_MAP[num_i]
                        for t in uids_l:
                            try:
                                H = await Emote_k(int(t), int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                await asyncio.sleep(0.1)
                            except Exception: pass
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Evo emote {num_i} sent", uid, chat_id, key, iv)
                    except Exception as e: print(f"Evo error: {e}")

                # ═══ /info ═══
                elif inPuTMsG.strip().startswith('/info '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        await safe_send_message(XX, f"[B][C][FFD700]🔍 Fetching info for {parts[1]}...", uid, chat_id, key, iv)
                        ok, data = await get_player_info(parts[1])
                        if ok:
                            msgs = format_player_info(data)
                            for m in msgs:
                                P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                await asyncio.sleep(2)
                        else:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ {data}", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]Usage: /info <uid>", uid, chat_id, key, iv)

                # ═══ /check ═══
                elif inPuTMsG.strip().startswith('/check '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        ok, result = await check_banned(parts[1])
                        reply = format_check_result(result) if ok else f"[B][C][FF0000]❌ {result}"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    else: await safe_send_message(XX, f"[B][C][FF0000]Usage: /check <uid>", uid, chat_id, key, iv)

                # ═══ /mth ═══
                elif inPuTMsG.strip().startswith('/mth'):
                    parts = inPuTMsG.strip().split(maxsplit=1)
                    if len(parts) < 2: await safe_send_message(XX, f"[B][C][FFFF00]Usage: /mth 2+2", uid, chat_id, key, iv)
                    else:
                        expr = parts[1].strip().replace("×", "*").replace("÷", "/").replace("x", "*")
                        try:
                            import re as _re
                            if not _re.match(r'^[\d\s\+\-\*\/\.\(\)\%]+$', expr): raise ValueError("Invalid expression")
                            result = eval(expr)
                            if isinstance(result, float) and result == int(result): result = int(result)
                            P = await SEndMsG(XX, f"[B][C][FFD700]🧮 Calculator\n\n[FFEA70]Expression: [FFFFFF]{expr}\n[DAA520]Result: [FFFFFF]{result}", uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        except ZeroDivisionError: await safe_send_message(XX, f"[B][C][FF0000]❌ Division by zero", uid, chat_id, key, iv)
                        except Exception: await safe_send_message(XX, f"[B][C][FF0000]❌ Invalid expression", uid, chat_id, key, iv)

                # ═══ /add ═══
                elif inPuTMsG.strip().startswith("/add ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await send_friend_request(parts[1], ToKen, region)
                            reply = f"[B][C][FFD700] {msg}"
                        except Exception as e: reply = f"[B][C][FF0000]Error: {e}"
                    else: reply = f"[B][C][FF0000]Usage: /add <uid>"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══ /remove ═══
                elif inPuTMsG.strip().startswith("/remove ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await remove_friend(parts[1], ToKen, region)
                            reply = f"[B][C][FFD700] {msg}"
                        except Exception as e: reply = f"[B][C][FF0000]Error: {e}"
                    else: reply = f"[B][C][FF0000]Usage: /remove <uid>"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══ /join ═══
                elif inPuTMsG.strip().startswith('/join '):
                    try:
                        code = inPuTMsG.split('/join ')[1].strip()
                        EM = await JoinSq_original(code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Joined squad: {code}", uid, chat_id, key, iv)
                    except Exception as e: print(f"Join error: {e}")

                # ═══ /exit /leave ═══
                elif inPuTMsG.startswith('/exit') or inPuTMsG.startswith('/leave'):
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(uid, key, iv))
                    await safe_send_message(XX, f"[B][C][FFD700]✅ Left squad", uid, chat_id, key, iv)

                # ═══ /5 ═══
                elif inPuTMsG.startswith('/5') and not inPuTMsG.startswith('/50'):
                    try:
                        await safe_send_message(XX, f"[B][C][FFD700]⚡ Creating 5-man team...", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(uid, key, iv))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq(5, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV(5, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][FFD700]✅ 5-man team invitation sent!", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team5 error: {e}")

                # ═══ /6 ═══
                elif inPuTMsG.startswith('/6'):
                    try:
                        await safe_send_message(XX, f"[B][C][FFD700]⚡ Creating 6-man team...", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(uid, key, iv))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq(6, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV(6, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][FFD700]✅ 6-man team invitation sent!", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team6 error: {e}")

                # ═══ /3 ═══
                elif inPuTMsG.startswith('/3') and not inPuTMsG.startswith('/30'):
                    try:
                        await safe_send_message(XX, f"[B][C][FFD700]⚡ Creating 3-man team...", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq(3, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV(3, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][FFD700]✅ 3-man team invitation sent!", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team3 error: {e}")

                # ═══ /4 ═══
                elif inPuTMsG.startswith('/4'):
                    try:
                        await safe_send_message(XX, f"[B][C][FFD700]⚡ Creating 4-man team...", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq(4, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV(4, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][FFD700]✅ 4-man team invitation sent!", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team4 error: {e}")

                # ═══ /spm ═══
                elif inPuTMsG.startswith('/spm '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        tgt = parts[1]
                        if tgt in spm_tasks: spm_tasks[tgt].cancel()
                        spam_targets.add(tgt); save_spam_targets()
                        spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Spam started for {tgt}", uid, chat_id, key, iv)
                    else: await safe_send_message(XX, f"[B][C][FF0000]Usage: /spm <uid>", uid, chat_id, key, iv)

                # ═══ /stp ═══
                elif inPuTMsG.startswith('/stp '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1] in spm_tasks:
                        spm_tasks[parts[1]].cancel(); del spm_tasks[parts[1]]
                        if parts[1] in spam_targets: spam_targets.remove(parts[1]); save_spam_targets()
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Spam stopped", uid, chat_id, key, iv)
                    else: await safe_send_message(XX, f"[B][C][FF0000]❌ No active spam", uid, chat_id, key, iv)

                # ═══ /gh ═══
                elif inPuTMsG.startswith('/gh '):
                    parts = inPuTMsG.split(' ', 2)
                    if len(parts) >= 3 and bot_uid is not None:
                        teamcode = parts[1].strip(); name = parts[2].strip()
                        try:
                            pending_ghost_future = asyncio.Future()
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await JoinSq_original(teamcode, key, iv))
                            try: await asyncio.wait_for(pending_ghost_future, timeout=8.0)
                            except asyncio.TimeoutError:
                                await safe_send_message(XX, f"[B][C][FF0000]❌ No response", uid, chat_id, key, iv)
                                pending_ghost_future = None; continue
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                            await asyncio.sleep(0.2)
                            for _ in range(4):
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await GhostPakcet(ghost_team_id, name, ghost_squad_code, key, iv))
                                await asyncio.sleep(0.1)
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Ghost joined as {name}", uid, chat_id, key, iv)
                            pending_ghost_future = None
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ {e}", uid, chat_id, key, iv)
                            pending_ghost_future = None

                # ═══ /msg ═══
                elif inPuTMsG.startswith('/msg '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 3: await safe_send_message(XX, f"[B][C][FF0000]Usage: /msg <text> <times>", uid, chat_id, key, iv)
                    else:
                        try:
                            times = int(parts[-1]); message = ' '.join(parts[1:-1])
                            if msg_spam_task and not msg_spam_task.done():
                                msg_spam_running = False; msg_spam_task.cancel(); await asyncio.sleep(0.1)
                            msg_spam_running = True
                            msg_spam_task = asyncio.create_task(msg_spam_loop(message, times, chat_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Sending {times}x: {message}", uid, chat_id, key, iv)
                        except ValueError: await safe_send_message(XX, f"[B][C][FF0000]Usage: /msg <text> <times>", uid, chat_id, key, iv)

                # ═══ /stop msg ═══
                elif inPuTMsG.strip() == '/stop msg':
                    if msg_spam_task and not msg_spam_task.done():
                        msg_spam_running = False; msg_spam_task.cancel()
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Msg spam stopped", uid, chat_id, key, iv)

                # ═══ /mg ═══
                elif inPuTMsG.startswith('/mg '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 2: await safe_send_message(XX, f"[B][C][FF0000]Usage: /mg <text> [repeats]", uid, chat_id, key, iv)
                    else:
                        try:
                            message = parts[1]; repeats = int(parts[2]) if len(parts) > 2 else 5
                            if repeats > 10: repeats = 10
                            if mg_spam_task and not mg_spam_task.done():
                                msg_spam_running = False; mg_spam_task.cancel(); await asyncio.sleep(0.1)
                            msg_spam_running = True
                            mg_spam_task = asyncio.create_task(send_wave_messages(message, repeats, chat_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Wave started: {message} x{repeats}", uid, chat_id, key, iv)
                        except ValueError: await safe_send_message(XX, f"[B][C][FF0000]Usage: /mg <text> [repeats]", uid, chat_id, key, iv)

                # ═══ /ban ═══
                elif inPuTMsG.startswith('/ban '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        if ban_task and not ban_task.done():
                            ban_running = False; ban_task.cancel(); ban_targets.clear(); await asyncio.sleep(0.3)
                        ban_targets.add(parts[1]); ban_task = asyncio.create_task(ban_loop(key, iv))
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Ban started on {parts[1]}", uid, chat_id, key, iv)
                    else: await safe_send_message(XX, f"[B][C][FF0000]Usage: /ban <uid>", uid, chat_id, key, iv)

                # ═══ /reject ═══
                elif inPuTMsG.startswith('/reject '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        if reject_spam_task and not reject_spam_task.done():
                            reject_spam_running = False; reject_spam_task.cancel(); await asyncio.sleep(0.3)
                        await safe_send_message(XX, f"[B][C][FFD700]🌀 Reject spam started on {parts[1]}", uid, chat_id, key, iv)
                        reject_spam_running = True
                        reject_spam_task = asyncio.create_task(reject_spam_loop(parts[1], key, iv))
                    else: await safe_send_message(XX, f"[B][C][FF0000]Usage: /reject <uid>", uid, chat_id, key, iv)

                # ═══ /reject_stop ═══
                elif inPuTMsG.strip() == '/reject_stop':
                    if reject_spam_task and not reject_spam_task.done():
                        reject_spam_running = False; reject_spam_task.cancel()
                        await safe_send_message(XX, f"[B][C][FFD700]✅ Reject spam stopped", uid, chat_id, key, iv)

                # ═══ /fast ═══
                elif inPuTMsG.startswith('/fast '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        uids = []; emote_id = None
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) > 3: uids.append(p)
                                else: emote_id = p
                        if uids and emote_id:
                            if fast_spam_task and not fast_spam_task.done():
                                fast_spam_running = False; fast_spam_task.cancel()
                            fast_spam_running = True
                            fast_spam_task = asyncio.create_task(fast_emote_spam(uids, emote_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Fast spam started", uid, chat_id, key, iv)

                # ═══ /p ═══
                elif inPuTMsG.startswith('/p '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 4:
                        try:
                            tgt = parts[1]; emote_id = parts[2]; times = int(parts[3])
                            if times > 100: times = 100
                            if custom_spam_task and not custom_spam_task.done():
                                custom_spam_running = False; custom_spam_task.cancel(); await asyncio.sleep(0.2)
                            custom_spam_running = True
                            custom_spam_task = asyncio.create_task(custom_emote_spam(tgt, emote_id, times, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Custom spam started: {emote_id} x{times}", uid, chat_id, key, iv)
                        except ValueError: await safe_send_message(XX, f"[B][C][FF0000]Usage: /p <uid> <emote> <times>", uid, chat_id, key, iv)

                # ═══ /title & /alltitles ═══
                elif inPuTMsG.strip().startswith('/title') or inPuTMsG.strip().startswith('/alltitles'):
                    titles_list = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015, 904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
                    await safe_send_message(XX, f"[B][C][FFD700]🎖️ Sending {len(titles_list)} titles...", uid, chat_id, key, iv)
                    for tid in titles_list:
                        try:
                            pkt = await convert_kyro_to_your_system(int(uid), chat_id, key, iv, nickname="DARK MASTER", title_id=tid)
                            if pkt and whisper_writer:
                                whisper_writer.write(pkt); await whisper_writer.drain()
                            await asyncio.sleep(2)
                        except Exception as e: print(f"Title error: {e}")
                    await safe_send_message(XX, f"[B][C][FFD700]✅ All titles sent!", uid, chat_id, key, iv)

                # ═══ /animation ═══
                elif inPuTMsG.strip().startswith('/animation'):
                    parts = inPuTMsG.strip().split()
                    anim_ids = {"1": 914000002, "2": 914000003, "3": 914038001, "4": 914039001, "5": 914042001, "6": 914044001, "7": 914047001, "8": 914047002, "9": 914048001, "10": 914050001, "11": 914051001, "12": 914053001}
                    if len(parts) < 2:
                        lst = "1-rampage\n2-cannibal\n3-devil\n4-scorpio\n5-frostfire\n6-paradox\n7-naruto\n8-aurora\n9-midnight\n10-itachi\n11-dreamspace\n12-eclipse"
                        await safe_send_message(XX, f"[B][C][FFD700]Animations:\n{lst}", uid, chat_id, key, iv)
                    elif parts[1] in anim_ids:
                        try:
                            pkt = await animation_packet(anim_ids[parts[1]], key, iv)
                            if pkt and online_writer:
                                online_writer.write(pkt); await online_writer.drain()
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Animation {parts[1]} sent!", uid, chat_id, key, iv)
                        except Exception as e: print(f"Anim error: {e}")
                    else: await safe_send_message(XX, f"[B][C][FF0000]❌ Animation not found", uid, chat_id, key, iv)

                # ═══ /b ═══
                elif inPuTMsG.strip().startswith('/b '):
                    parts = inPuTMsG.strip().split()
                    bundle_ids = {"1": 914000002, "2": 914000003, "3": 914038001, "4": 914039001, "5": 914042001, "6": 914044001, "7": 914047001, "8": 914047002, "9": 914048001, "10": 914050001, "11": 914051001, "12": 914053001}
                    if len(parts) < 2: await safe_send_message(XX, f"[B][C][FFD700]Usage: /b <1-12>", uid, chat_id, key, iv)
                    elif parts[1] in bundle_ids:
                        bid = bundle_ids[parts[1]]
                        try:
                            anim_pkt = await animation_packet(bid, key, iv)
                            if anim_pkt and online_writer:
                                online_writer.write(anim_pkt); await online_writer.drain()
                            await asyncio.sleep(3)
                            b_pkt = await Look_Changer(bid, key, iv, look_type=1, region=region)
                            if b_pkt and online_writer:
                                online_writer.write(b_pkt); await online_writer.drain()
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Bundle {parts[1]} sent!", uid, chat_id, key, iv)
                        except Exception as e: print(f"Bundle error: {e}")
                    else: await safe_send_message(XX, f"[B][C][FF0000]❌ Bundle not found", uid, chat_id, key, iv)

                # ═══ /sticker ═══
                elif inPuTMsG.strip().startswith('/sticker'):
                    try:
                        pkt = await send_sticker_packet(uid, chat_id, key, iv)
                        if pkt and whisper_writer:
                            whisper_writer.write(pkt); await whisper_writer.drain()
                    except Exception as e: print(f"Sticker error: {e}")

                # ═══ /ice ═══
                elif inPuTMsG.strip().startswith('/ice '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2:
                        tgt = parts[1] if parts[1].lower() not in ('me', 'self') else str(uid)
                        if freeze_task and not freeze_task.done():
                            freeze_running = False; freeze_task.cancel(); await asyncio.sleep(0.3)
                        freeze_running = True
                        freeze_task = asyncio.create_task(freeze_emote_spam(tgt, key, iv, region, XX, chat_id, uid))
                        await safe_send_message(XX, f"[B][C][FFD700]❄️ Freeze started {tgt}", uid, chat_id, key, iv)

                # ═══ /room ═══
                elif inPuTMsG.strip().startswith('/room '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        tgt = parts[1]; rid = parts[2]
                        try:
                            for i in range(3000):
                                spam_p = await Room_Spam(tgt, rid, "DARK MASTER", key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', spam_p)
                                if (i + 1) % 50 == 0: print(f"Room spam progress: {i+1}/3000")
                                await asyncio.sleep(0.05)
                            await safe_send_message(XX, f"[B][C][FFD700]✅ Room spam completed", uid, chat_id, key, iv)
                        except Exception as e: print(f"Room spam error: {e}")

                else:
                    pass

            writer.close(); await writer.wait_closed(); whisper_writer = None
        except Exception as e:
            print(f"Chat error: {ip}:{port} - {e}")
            whisper_writer = None
        await asyncio.sleep(reconnect_delay)