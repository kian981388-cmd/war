from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import os
import time
import random
from html import escape
from datetime import date

app = Flask(__name__)
app.secret_key = "war_bot_secure_key_107"

DB_FILE = "war_game_db.json"
CHAT_FILE = "chat_db.json"
GIFT_FILE = "gift_codes.json"

BASE_MAX_HP = 10000
DAILY_SALARY = 1500
BASE_ATTACK_COOLDOWN = 60 
MINER_INCOME = 400 

VALID_COUNTRIES = ["ایران", "افغانستان", "ترکیه", "آمریکا", "انگلیس", "آلمان", "فرانسه", "روسیه", "چین", "ژاپن", "کانادا", "استرالیا", "برزیل", "مصر", "عربستان", "عراق", "سوریه", "لبنان", "پاکستان", "هند", "کره جنوبی", "کره شمالی", "ایتالیا", "اسپانیا", "پرتغال", "هلند", "سوئد", "نروژ", "فنلاند", "دانمارک", "سوئیس", "اتریش", "بلژیک", "یونان", "مکزیک", "آرژانتین", "کلمبیا", "شیلی", "پرو", "ونزوئلا", "کوبا", "آفریقای جنوبی", "نیجریه", "کنیا", "اندونزی", "مالزی", "تایلند", "ویتنام", "فیلیپین", "سنگاپور"]
BAD_WORDS = ["کص", "کیر", "کس", "لاشی", "جنده", "کونی", "خر", "گوه"]

TASK_POOL = [
    {"id": "t1", "name": "۳ بار حمله کن", "type": "attacks", "target": 3, "reward": 2000},
    {"id": "t2", "name": "۵ بار از فروشگاه خرید کن", "type": "buys", "target": 5, "reward": 3000},
    {"id": "t3", "name": "۲ نفر را نابود کن", "type": "kills", "target": 2, "reward": 5000},
    {"id": "t4", "name": "۱ بار جاسوسی کن", "type": "spy", "target": 1, "reward": 1500},
    {"id": "t5", "name": "۱۰,۰۰۰ تومان خرج کن", "type": "spent", "target": 10000, "reward": 2000},
    {"id": "t6", "name": "۵ بار حمله کن", "type": "attacks", "target": 5, "reward": 4000},
    {"id": "t7", "name": "۱۰ بار از فروشگاه خرید کن", "type": "buys", "target": 10, "reward": 6000},
    {"id": "t8", "name": "۳ نفر را نابود کن", "type": "kills", "target": 3, "reward": 8000},
    {"id": "t9", "name": "۲ بار جاسوسی کن", "type": "spy", "target": 2, "reward": 2500},
    {"id": "t10", "name": "۵۰,۰۰۰ تومان خرج کن", "type": "spent", "target": 50000, "reward": 10000},
    {"id": "t11", "name": "۱ بار حقوق روزانه بگیر", "type": "daily", "target": 1, "reward": 1000},
    {"id": "t12", "name": "۱ بار نفت بفروش", "type": "sell_oil", "target": 1, "reward": 2000},
    {"id": "t13", "name": "۱۰ بار حمله کن", "type": "attacks", "target": 10, "reward": 8000},
    {"id": "t14", "name": "۲۰ بار از فروشگاه خرید کن", "type": "buys", "target": 20, "reward": 12000},
    {"id": "t15", "name": "۵ نفر را نابود کن", "type": "kills", "target": 5, "reward": 15000},
    {"id": "t16", "name": "۵ بار جاسوسی کن", "type": "spy", "target": 5, "reward": 5000},
    {"id": "t17", "name": "۱۰۰,۰۰۰ تومان خرج کن", "type": "spent", "target": 100000, "reward": 20000},
    {"id": "t18", "name": "۲ بار حقوق روزانه بگیر", "type": "daily", "target": 2, "reward": 2000},
    {"id": "t19", "name": "۳ بار نفت بفروش", "type": "sell_oil", "target": 3, "reward": 5000},
    {"id": "t20", "name": "۲۰ بار حمله کن", "type": "attacks", "target": 20, "reward": 15000},
    {"id": "t21", "name": "۵۰ بار از فروشگاه خرید کن", "type": "buys", "target": 50, "reward": 30000},
    {"id": "t22", "name": "۱۰ نفر را نابود کن", "type": "kills", "target": 10, "reward": 25000},
    {"id": "t23", "name": "۱۰ بار جاسوسی کن", "type": "spy", "target": 10, "reward": 10000},
    {"id": "t24", "name": "۲۰۰,۰۰۰ تومان خرج کن", "type": "spent", "target": 200000, "reward": 40000},
    {"id": "t25", "name": "۳ بار حقوق روزانه بگیر", "type": "daily", "target": 3, "reward": 3000},
    {"id": "t26", "name": "۵ بار نفت بفروش", "type": "sell_oil", "target": 5, "reward": 8000},
    {"id": "t27", "name": "۳۰ بار حمله کن", "type": "attacks", "target": 30, "reward": 20000},
    {"id": "t28", "name": "۱۰۰ بار از فروشگاه خرید کن", "type": "buys", "target": 100, "reward": 50000},
    {"id": "t29", "name": "۲۰ نفر را نابود کن", "type": "kills", "target": 20, "reward": 50000},
    {"id": "t30", "name": "۵۰۰,۰۰۰ تومان خرج کن", "type": "spent", "target": 500000, "reward": 100000},
]

def get_daily_tasks():
    today = int(time.time() // 86400)
    r = random.Random(today)
    return r.sample(TASK_POOL, 3)

def get_black_market_items():
    today = int(time.time() // 86400)
    r = random.Random(today * 2)
    keys = list(SHOP_ITEMS.keys())
    selected = r.sample(keys, 3)
    items = {}
    for k in selected:
        item = SHOP_ITEMS[k].copy()
        discount = r.choice([20, 30, 40, 50])
        item['price'] = int(item['price'] * (1 - discount/100))
        item['discount'] = discount
        items[k] = item
    return items

def format_shield_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0: return f"{h} ساعت و {m} دقیقه"
    return f"{m} دقیقه"

def has_profanity(text):
    text = text.lower()
    return any(word in text for word in BAD_WORDS)

SHOP_ITEMS = {
    "m_ballistic": {"name": "🚀 موشک بالستیک", "price": 100, "dmg": 100, "type": "missile", "desc": "دمیج: 100"},
    "m_hypersonic": {"name": "☄️ موشک هایپرسونیک", "price": 150, "dmg": 150, "type": "missile", "desc": "دمیج: 150"},
    "m_nuclear": {"name": "☢️ موشک اتم", "price": 5000, "dmg": 5000, "type": "missile", "desc": "دمیج: 5000"},
    "m_cruise": {"name": "✈️ موشک کروز", "price": 350, "dmg": 250, "type": "missile", "desc": "دمیج: 250"},
    "m_cluster": {"name": "💥 موشک خوشه‌ای", "price": 500, "dmg": 400, "type": "missile", "desc": "دمیج: 400"},
    "f14": {"name": "✈️ جنگنده F-14", "price": 3500, "dmg": 1500, "type": "fighter", "desc": "دمیج: 1500"},
    "su57": {"name": "✈️ جنگنده Su-57", "price": 7000, "dmg": 3500, "type": "fighter", "desc": "دمیج: 3500"},
    "b2": {"name": "✈️ بمب‌افکن B-2", "price": 10000, "dmg": 6000, "type": "fighter", "desc": "دمیج: 6000"},
    "apache": {"name": "🚁 بالگرد آپاچی", "price": 4000, "dmg": 2000, "type": "fighter", "desc": "دمیج: 2000"},
    "s_destroyer": {"name": "🚢 ناوشکن", "price": 12000, "dmg": 4000, "type": "ship", "desc": "دمیج: 4000"},
    "s_submarine": {"name": "🤿 زیردریایی", "price": 20000, "dmg": 6000, "type": "ship", "desc": "دمیج: 6000"},
    "s_carrier": {"name": "🛳 ناو هواپیمابر", "price": 35000, "dmg": 8000, "type": "ship", "desc": "دمیج: 8000"},
    "s_nuclear": {"name": "⚓ ناو هسته‌ای", "price": 60000, "dmg": 20000, "type": "ship", "desc": "دمیج: 20000"},
    "g_normal": {"name": "🪖 نیروی زمینی عادی", "price": 10000, "dmg": 3000, "type": "ground", "desc": "دمیج: 3000"},
    "g_armored": {"name": "🛡 نیروی زمینی زره‌پوش", "price": 20000, "dmg": 7000, "type": "ground", "desc": "دمیج: 7000"},
    "g_special": {"name": "⭐ نیروی ویژه", "price": 30000, "dmg": 12000, "type": "ground", "desc": "دمیج: 12000"},
    "def_1": {"name": "🛡 پدافند زمینی 1", "price": 1000, "hp": 1000, "type": "defense", "desc": "سلامتی: 1000"},
    "def_2": {"name": "🛡 پدافند زمینی 2", "price": 2000, "hp": 2500, "type": "defense", "desc": "سلامتی: 2500"},
    "def_3": {"name": "🛡 پدافند زمینی 3", "price": 5000, "hp": 6000, "type": "defense", "desc": "سلامتی: 6000"},
    "def_4": {"name": "🔫 پدافند لیزری", "price": 8000, "hp": 8000, "type": "defense", "desc": "سلامتی: 8000"},
    "def_5": {"name": "🛰 سپر ماهواره‌ای", "price": 12000, "hp": 10000, "type": "defense", "desc": "سلامتی: 10000"},
    "nd_patrol": {"name": "⛵ ناوچه گشتی", "price": 3000, "hp": 2000, "type": "naval_def", "desc": "دفاع دریایی"},
    "nd_mine": {"name": "💣 میدان مین", "price": 5000, "hp": 4000, "type": "naval_def", "desc": "دفاع دریایی"},
    "nd_sonar": {"name": "📡 سونار", "price": 8000, "hp": 3000, "type": "naval_def", "desc": "دفاع دریایی"},
    "nd_coastal": {"name": "🏖 پدافند ساحلی", "price": 10000, "hp": 8000, "type": "naval_def", "desc": "دفاع دریایی"},
    "nd_escort": {"name": "🛳 ناوشکن اسکورت", "price": 15000, "hp": 10000, "type": "naval_def", "desc": "دفاع دریایی"},
    "nd_aegis": {"name": "🛰 AEGIS", "price": 25000, "hp": 20000, "type": "naval_def", "desc": "دفاع دریایی"},
    "box_epic": {"name": "🎁 باکس اپیک", "price": 3000, "type": "box", "desc": "جایزه شانسی"},
    "box_legendary": {"name": "🎁 باکس لجندی", "price": 6000, "type": "box", "desc": "جایزه شانسی"},
    "box_mythic": {"name": "🎁 باکس متیک", "price": 10000, "type": "box", "desc": "جایزه شانسی"},
    "miner": {"name": "⛏ ماینر", "price": 12000, "type": "building", "desc": "درآمد پسیو"},
    "hospital": {"name": "🏥 بیمارستان", "price": 8000, "type": "building", "desc": "درمان"},
    "factory": {"name": "🏭 کارخانه", "price": 5000, "type": "building", "desc": "درآمد روزانه"},
    "school": {"name": "🏫 مدرسه", "price": 3000, "type": "building", "desc": "درآمد روزانه"},
    "apartment": {"name": "🏢 آپارتمان", "price": 1000, "type": "building", "desc": "درآمد روزانه"},
    "gold_mine": {"name": "🪙 معدن طلا", "price": 25000, "type": "building", "desc": "درآمد روزانه"},
    "refinery": {"name": "🏭 پالایشگاه", "price": 20000, "type": "building", "desc": "افزایش قیمت نفت"},
    "cmd_center": {"name": "🏛 مرکز فرماندهی", "price": 15000, "type": "special", "desc": "کول‌داون نصف + ایکس‌پی بیشتر"},
    "oil_kit_1": {"name": "🛢 تجهیزات نفت 1", "price": 5000, "type": "oil", "desc": "تولید ۵ بشکه در ساعت"},
    "oil_kit_2": {"name": "🛢 تجهیزات نفت 2", "price": 15000, "type": "oil", "desc": "تولید ۱۵ بشکه در ساعت"},
    "oil_kit_3": {"name": "🛢 تجهیزات نفت 3", "price": 40000, "type": "oil", "desc": "تولید ۵۰ بشکه در ساعت"},
    "vip": {"name": "💎 کارت VIP", "price": 45000, "type": "special", "desc": "شیلد ۴۸ ساعته + درآمد ۲ برابر"},
    "dozhband": {"name": "🏰 دژبند", "price": 20000, "type": "special", "desc": "افزایش جان به 15000"},
    "heal_kit": {"name": "💉 کیت درمان", "price": 1500, "type": "special", "desc": "ترمیم ۱۰۰۰ جان"},
    "repair_kit": {"name": "🔧 کیت تعمیرات", "price": 1500, "type": "special", "desc": "ترمیم کامل پدافند"},
    "shield_1": {"name": "🔮 شیلد 1 (1 ساعت)", "price": 250, "type": "shield", "desc": "دفع حملات"},
    "shield_2": {"name": "🔮 شیلد 2 (2 ساعت)", "price": 500, "type": "shield", "desc": "دفع حملات"},
    "shield_3": {"name": "🔮 شیلد 3 (24 ساعت)", "price": 1000, "type": "shield", "desc": "دفع حملات"},
}

def load_db(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if file == CHAT_FILE and not isinstance(data, list): return []
                return data
        except: pass
    return [] if file == CHAT_FILE else {}

def save_db(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

players_db = load_db(DB_FILE)
chat_db = load_db(CHAT_FILE)
gift_db = load_db(GIFT_FILE)

def get_player_stats(player):
    today = str(date.today())
    if player.get("stats_date") != today:
        player["stats_date"] = today
        player["daily_stats"] = {"attacks": 0, "buys": 0, "kills": 0, "spy": 0, "spent": 0, "daily": 0, "sell_oil": 0}
        player["tasks_claimed"] = []
    return player.get("daily_stats", {})

def update_passive_income(player):
    now = time.time()
    last_check = player.get("last_miner_check", now)
    hours_passed = int((now - last_check) // 3600)
    if hours_passed > 0:
        if player.get("miners", 0) > 0:
            income = hours_passed * player["miners"] * MINER_INCOME
            if player.get("shield_until", 0) > now: income *= 2
            player["money"] += income
        if player.get("oil_level", 0) > 0:
            player["oil"] = player.get("oil", 0) + (hours_passed * {1: 5, 2: 15, 3: 50}.get(player.get("oil_level", 0), 0))
        if player.get("hospitals", 0) > 0:
            player["hp"] = min(player.get("max_hp", BASE_MAX_HP), player["hp"] + (hours_passed * 500 * player["hospitals"]))
        player["last_miner_check"] = now
        save_db(players_db, DB_FILE)

BASE_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>WAR BOT</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
    <style>
        * { box-sizing: border-box; font-family: 'Vazirmatn', sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #0b1120; color: #e2e8f0; margin: 0; padding: 0; padding-bottom: 70px; overflow-x: hidden; }
        
        #toast-container { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; display: flex; flex-direction: column; gap: 10px; align-items: center; width: 100%; pointer-events: none;}
        .toast { background: #111827; border: 2px solid #00d2ff; color: #00d2ff; padding: 12px 25px; border-radius: 10px; font-weight: bold; box-shadow: 0 4px 15px rgba(0,210,255,0.3); animation: slideDown 0.3s ease-out; font-size: 14px;}
        .toast.error { border-color: #ef4444; color: #ef4444; box-shadow: 0 4px 15px rgba(239,68,68,0.3); }
        @keyframes slideDown { from { top: -50px; opacity: 0; } to { top: 20px; opacity: 1; } }
        
        .top-bar { display: flex; justify-content: space-between; align-items: center; background: #111827; padding: 15px 20px; border-bottom: 1px solid #1f2937; position: sticky; top: 0; z-index: 100; }
        .profile-icon { width: 40px; height: 40px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; border: 2px solid #00d2ff; color: #fff;}
        .coins-badge { background: #1f2937; padding: 8px 15px; border-radius: 20px; color: #fbbf24; font-weight: bold; display: flex; align-items: center; gap: 5px; border: 1px solid #374151;}
        .menu-btn { font-size: 24px; cursor: pointer; color: #9ca3af; }

        .side-menu { position: fixed; top: 0; right: -250px; width: 250px; height: 100%; background: #111827; z-index: 200; transition: 0.3s; padding: 20px; box-shadow: -5px 0 15px rgba(0,0,0,0.5); border-left: 1px solid #1f2937; }
        .side-menu.open { right: 0; }
        .side-menu a { display: block; color: #e2e8f0; text-decoration: none; padding: 15px 0; border-bottom: 1px solid #1f2937; font-size: 16px; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 150; display: none; }
        .overlay.open { display: block; }

        .container { padding: 20px; max-width: 500px; margin: 0 auto; }
        
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 20px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }
        
        input, select { width: 100%; padding: 15px; margin: 10px 0; background: #1f2937; border: 1px solid #374151; color: #fff; border-radius: 12px; font-family: 'Vazirmatn'; font-size: 15px; outline: none; }
        input:focus, select:focus { border-color: #00d2ff; }
        
        button { width: 100%; padding: 15px; margin: 5px 0; background: linear-gradient(135deg, #00d2ff 0%, #0088cc 100%); color: #fff; border: none; border-radius: 12px; font-family: 'Vazirmatn'; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3); transition: transform 0.1s; }
        button:active { transform: scale(0.97); }
        .btn-red { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
        .btn-green { background: linear-gradient(135deg, #22c55e 0%, #15803d 100%); box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3); }
        .btn-gold { background: linear-gradient(135deg, #fbbf24 0%, #b45309 100%); box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3); }
        .btn-black { background: linear-gradient(135deg, #333 0%, #111 100%); border: 1px solid #444; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }

        .shop-item { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f2937; padding: 15px 0; }
        .shop-item:last-child { border-bottom: none; }
        .btn-buy { width: auto; padding: 8px 20px; margin: 0; font-size: 14px; border-radius: 10px; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #111827; display: flex; justify-content: space-around; align-items: center; padding: 8px 0; border-top: 1px solid #1f2937; z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #6b7280; text-decoration: none; font-size: 10px; gap: 4px; transition: 0.3s; }
        .nav-item.active { color: #00d2ff; }
        .nav-icon { font-size: 20px; }

        .chat-box { height: 400px; overflow-y: auto; background: #1f2937; padding: 15px; border-radius: 15px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px;}
        .chat-msg { background: #374151; padding: 10px 15px; border-radius: 15px; border-bottom-right-radius: 0; width: fit-content; max-width: 80%; }
        .chat-name { color: #00d2ff; font-weight: bold; font-size: 12px; margin-bottom: 3px; display: block;}
        .chat-text { color: #fff; font-size: 14px; }
        
        .help-title { color: #00d2ff; border-bottom: 1px solid #00d2ff; padding-bottom: 5px; margin-top: 25px; font-size: 18px;}
        .help-text { line-height: 1.8; color: #9ca3af; font-size: 14px; }
        .highlight { color: #fbbf24; font-weight: bold; }

        .stat-box { background: #1f2937; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; }
        .stat-val { font-size: 20px; font-weight: bold; color: #00d2ff; }
        .stat-label { font-size: 12px; color: #9ca3af; }

        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 12px; text-align: center; background: #1f2937; border: 1px solid #374151; border-radius: 12px; font-weight: bold; cursor: pointer; transition: 0.3s; color: #9ca3af; }
        .tab-btn.active { background: #00d2ff; color: #000; border-color: #00d2ff; box-shadow: 0 0 15px rgba(0, 210, 255, 0.4); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .equip-category { margin-bottom: 15px; }
        .equip-category h4 { color: #fbbf24; margin-bottom: 10px; border-bottom: 1px solid #374151; padding-bottom: 5px;}
        .equip-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .equip-item { background: #1f2937; padding: 10px; border-radius: 8px; font-size: 13px; display: flex; justify-content: space-between; }
    </style>
</head>
<body>
    <div id="toast-container"></div>

    {% if session.get('user_id') %}
    <div class="top-bar">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div class="profile-icon">{{ p.name[0]|upper }}</div>
            <div class="coins-badge">🪙 <span id="top-coins">{{ p.money }}</span></div>
        </div>
        <div class="menu-btn" onclick="toggleMenu()">☰</div>
    </div>
    {% endif %}

    <div class="overlay" id="overlay" onclick="toggleMenu()"></div>
    <div class="side-menu" id="side-menu">
        <h3 style="color: #00d2ff; margin-top: 0;">منوی بیشتر</h3>
        <a href="/spy">🕵️‍♂️ سیستم جاسوسی</a>
        <a href="/transfer">💸 انتقال پول</a>
        <a href="/gift">🎁 کد هدیه</a>
        <a href="/secret">🔑 دستورات ویژه</a>
        <a href="/help">📖 راهنمای بازی</a>
        <a href="/logout" style="color: #ef4444;">🚪 خروج</a>
    </div>

    <div class="container">
        {{ content | safe }}
    </div>

    {% if session.get('user_id') %}
    <div class="bottom-nav">
        <a href="/" class="nav-item {% if request.path == '/' %}active{% endif %}"><span class="nav-icon">🏠</span><span>خانه</span></a>
        <a href="/shop" class="nav-item {% if request.path == '/shop' %}active{% endif %}"><span class="nav-icon">🛒</span><span>فروشگاه</span></a>
        <a href="/attack" class="nav-item {% if request.path == '/attack' %}active{% endif %}"><span class="nav-icon">⚔️</span><span>حمله</span></a>
        <a href="/tasks" class="nav-item {% if request.path == '/tasks' %}active{% endif %}"><span class="nav-icon">📋</span><span>تسک‌ها</span></a>
        <a href="/chat" class="nav-item {% if request.path == '/chat' %}active{% endif %}"><span class="nav-icon">💬</span><span>چت</span></a>
        <a href="/leaderboard" class="nav-item {% if request.path == '/leaderboard' %}active{% endif %}"><span class="nav-icon">🏆</span><span>لیدربرد</span></a>
    </div>
    {% endif %}

    <script>
        function toggleMenu() {
            document.getElementById('side-menu').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('open');
        }
        
        function showToast(message, isError = false) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast' + (isError ? ' error' : '');
            toast.innerText = message;
            container.appendChild(toast);
            setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.5s'; }, 2500);
            setTimeout(() => { toast.remove(); }, 3000);
        }

        function buyItem(itemKey, isBlackMarket=false) {
            const endpoint = isBlackMarket ? '/buy_black_market' : '/buy';
            fetch(endpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({item: itemKey})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    showToast(data.msg, false);
                    document.getElementById('top-coins').innerText = data.new_money;
                } else {
                    showToast(data.msg, true);
                }
            });
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }
    </script>
</body>
</html>
"""

LOGIN_HTML = """
<div class="card" style="margin-top: 50px;">
    <h2 style="text-align: center; color: #00d2ff;">ورود به حساب</h2>
    <form method="POST">
        <input type="text" name="name" placeholder="نام کاربری" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button type="submit">ورود</button>
    </form>
    <div style="text-align: center; margin-top: 15px;">
        <a href="/signup" style="color: #00d2ff; text-decoration: none;">اکانت ندارید؟ ثبت‌نام کنید</a>
    </div>
</div>
"""

SIGNUP_HTML = """
<div class="card" style="margin-top: 50px;">
    <h2 style="text-align: center; color: #00d2ff;">ساخت اکانت</h2>
    {% if error %}<p style="color: #ef4444; text-align: center;">{{ error }}</p>{% endif %}
    <form method="POST">
        <input type="text" name="name" placeholder="نام شما" required>
        <input type="text" name="country" placeholder="کشور (مثلا ایران)" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button type="submit">ثبت‌نام</button>
    </form>
    <div style="text-align: center; margin-top: 15px;">
        <a href="/login" style="color: #00d2ff; text-decoration: none;">قبلاً ثبت‌نام کرده‌اید؟</a>
    </div>
</div>
"""

HOME_HTML = """
<div class="card" style="text-align: center;">
    <h2 style="color: #00d2ff; margin-top: 0;">{{ p.name }}</h2>
    <p style="color: #9ca3af; margin-bottom: 15px;">شناسه: <b style="color: #fff;">{{ p.id }}</b> | کشور: <b style="color: #fff;">{{ p.country }}</b></p>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
        <div class="stat-box">
            <div class="stat-val">{{ p.hp }} / {{ p.max_hp }}</div>
            <div class="stat-label">❤️ جان</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="font-size: 14px;">{{ p.shield_status }}</div>
            <div class="stat-label">🛡 شیلد</div>
        </div>
        <div class="stat-box">
            <div class="stat-val">Level {{ p.get('level', 1) }}</div>
            <div class="stat-label">XP: {{ p.get('xp', 0) }} / {{ next_xp }}</div>
        </div>
        <div class="stat-box">
            <div class="stat-val">{{ p.oil }}</div>
            <div class="stat-label">🛢 نفت</div>
        </div>
    </div>
    
    <div style="background: #1f2937; border-radius: 12px; padding: 15px; text-align: right; font-size: 14px; margin-bottom: 15px;">
        <div style="margin-bottom: 5px;">🛡 <b>پدافند زمینی:</b> {{ p.defense_name }} (HP: {{ p.defense_hp }})</div>
        <div>⚓ <b>پدافند دریایی:</b> {{ p.naval_defense_name }} (HP: {{ p.naval_defense_hp }})</div>
    </div>
</div>

<div class="card" style="text-align: right;">
    <h3 style="color: #00d2ff; margin-top: 0; border-bottom: 1px solid #1f2937; padding-bottom: 10px;">🎒 تجهیزات شما</h3>
    
    <div class="equip-category">
        <h4>⚔️ تجهیزات جنگی</h4>
        <div class="equip-grid">
            {% set ns1 = namespace(has=false) %}
            {% for key, count in p.get('inv', {}).items() %}
                {% if count > 0 and key in items and items[key].type in ['missile', 'fighter', 'ship', 'ground'] %}
                    {% set ns1.has = true %}
                    <div class="equip-item">
                        <span>{{ items[key].name }}</span>
                        <b style="color: #fbbf24;">{{ count }}</b>
                    </div>
                {% endif %}
            {% endfor %}
            {% if not ns1.has %}<p style="color: #6b7280; font-size: 12px;">خالی</p>{% endif %}
        </div>
    </div>

    <div class="equip-category">
        <h4>🛡 پدافندها</h4>
        <div class="equip-grid">
            {% set ns2 = namespace(has=false) %}
            
            {% if p.get('defense', 0) > 0 %}
                {% set ns2.has = true %}
                <div class="equip-item">
                    <span>{{ items['def_' + p.defense|string].name }}</span>
                    <b style="color: #fbbf24;">HP: {{ p.defense_hp }}</b>
                </div>
            {% endif %}
            
            {% if p.get('naval_defense') %}
                {% set ns2.has = true %}
                <div class="equip-item">
                    <span>{{ items[p.naval_defense].name }}</span>
                    <b style="color: #fbbf24;">HP: {{ p.naval_defense_hp }}</b>
                </div>
            {% endif %}
            
            {% if not ns2.has %}<p style="color: #6b7280; font-size: 12px;">خالی</p>{% endif %}
        </div>
    </div>

    <div class="equip-category">
        <h4>🏗 ساختمان‌ها</h4>
        <div class="equip-grid">
            {% set ns3 = namespace(has=false) %}
            {% if p.get('miners', 0) > 0 %}
                {% set ns3.has = true %}
                <div class="equip-item"><span>⛏ ماینر</span><b style="color: #fbbf24;">{{ p.miners }}</b></div>
            {% endif %}
            {% if p.get('hospitals', 0) > 0 %}
                {% set ns3.has = true %}
                <div class="equip-item"><span>🏥 بیمارستان</span><b style="color: #fbbf24;">{{ p.hospitals }}</b></div>
            {% endif %}
            {% if p.get('refineries', 0) > 0 %}
                {% set ns3.has = true %}
                <div class="equip-item"><span>🏭 پالایشگاه</span><b style="color: #fbbf24;">{{ p.refineries }}</b></div>
            {% endif %}
            {% for b_key, b_count in p.get('buildings', {}).items() %}
                {% if b_count > 0 %}
                    {% set ns3.has = true %}
                    <div class="equip-item"><span>{{ items[b_key].name }}</span><b style="color: #fbbf24;">{{ b_count }}</b></div>
                {% endif %}
            {% endfor %}
            {% if not ns3.has %}<p style="color: #6b7280; font-size: 12px;">خالی</p>{% endif %}
        </div>
    </div>

    <div class="equip-category">
        <h4>🛢 نفت</h4>
        <div class="equip-grid">
            {% set ns4 = namespace(has=false) %}
            {% if p.get('oil_level', 0) > 0 %}
                {% set ns4.has = true %}
                <div class="equip-item"><span>تجهیزات نفت سطح {{ p.oil_level }}</span><b style="color: #fbbf24;">فعال</b></div>
            {% endif %}
            {% if not ns4.has %}<p style="color: #6b7280; font-size: 12px;">خالی</p>{% endif %}
        </div>
    </div>
</div>

<div class="card" style="text-align: right; font-size: 14px;">
    <h3 style="color: #fbbf24; margin-top: 0; border-bottom: 1px solid #374151; padding-bottom: 10px;">📊 آمار من</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div>🏆 بردها: <b style="color: #22c55e;">{{ p.get('wins', 0) }}</b></div>
        <div>💀 باخت‌ها: <b style="color: #ef4444;">{{ p.get('losses', 0) }}</b></div>
        <div>☠️ کشته‌ها: <b>{{ p.get('kills', 0) }}</b></div>
        <div>💥 خسارت: <b>{{ p.get('damage', 0) }}</b></div>
    </div>
</div>

<button class="btn-green" onclick="location.href='/daily'">💵 دریافت حقوق روزانه</button>
<button class="btn-gold" onclick="location.href='/sell_oil'">💸 فروش تمام نفت‌ها</button>
"""

SHOP_HTML = """
<h2 style="color: #00d2ff; text-align: center;">🛒 بازار تسلیحات</h2>

<div class="tabs">
    <div class="tab-btn active" onclick="switchTab('tab-main')">فروشگاه اصلی</div>
    <div class="tab-btn" onclick="switchTab('tab-black')" style="color: #ef4444; border-color: #ef4444;">بازار سیاه</div>
</div>

<div id="tab-main" class="tab-content active">
    <div class="card">
        {% for key, item in items.items() %}
        <div class="shop-item">
            <div>
                <div style="font-weight: bold; color: #fff;">{{ item.name }}</div>
                <div style="font-size: 12px; color: #9ca3af;">{{ item.desc }}</div>
                <div style="font-size: 13px; color: #fbbf24;">{{ item.price }} تومان</div>
            </div>
            <button class="btn-buy" onclick="buyItem('{{ key }}', false)">خرید</button>
        </div>
        {% endfor %}
    </div>
</div>

<div id="tab-black" class="tab-content">
    <div class="card" style="border-color: #ef4444;">
        <p style="color: #ef4444; text-align: center; font-size: 13px;">آیتم‌های زیر فقط تا پایان امروز در دسترس هستند!</p>
        {% for key, item in black_market.items() %}
        <div class="shop-item">
            <div>
                <div style="font-weight: bold; color: #fff;">{{ item.name }} <span style="color: #ef4444; font-size: 12px;">({{ item.discount }}% تخفیف)</span></div>
                <div style="font-size: 12px; color: #9ca3af;">{{ item.desc }}</div>
                <div style="font-size: 13px;">
                    <span style="text-decoration: line-through; color: #6b7280;">{{ item.price }} تومان</span>
                    <b style="color: #22c55e; margin-right: 5px;">{{ item.price }} تومان</b>
                </div>
            </div>
            <button class="btn-red btn-buy" onclick="buyItem('{{ key }}', true)">خرید</button>
        </div>
        {% endfor %}
    </div>
</div>
"""

ATTACK_HTML = """
<h2 style="color: #ef4444; text-align: center;">⚔️ اتاق جنگ</h2>
<div class="card">
    {% if msg %}<div style="background: #1f2937; border-left: 4px solid #00d2ff; padding: 15px; margin-bottom: 15px; color: #fff;">{{ msg }}</div>{% endif %}
    {% if has_weapons %}
    <form method="POST">
        <label style="font-size: 14px; color: #9ca3af;">شناسه دشمن:</label>
        <input type="text" name="target_id" placeholder="مثلا 1024" required>
        
        <label style="font-size: 14px; color: #9ca3af;">سلاح مورد استفاده:</label>
        <select name="weapon">
            {% for w_key, w_name in weapons %}
                <option value="{{ w_key }}">{{ w_name }}</option>
            {% endfor %}
        </select>
        
        <label style="font-size: 14px; color: #9ca3af;">تعداد شلیک (رگبار):</label>
        <input type="number" name="quantity" value="1" min="1" required>
        
        <button type="submit" class="btn-red" style="margin-top: 15px;">🚀 شلیک کن!</button>
    </form>
    {% else %}
    <div style="text-align: center; padding: 20px;">
        <p style="color: #ef4444;">⚠️ شما هیچ سلاحی در انبار ندارید!</p>
        <button onclick="location.href='/shop'">برو به فروشگاه</button>
    </div>
    {% endif %}
</div>
"""

LEADERBOARD_HTML = """
<h2 style="color: #fbbf24; text-align: center;">🏆 برترین‌ها</h2>
<div class="card">
    {% for u in top %}
    <div class="shop-item">
        <div style="color: #fff;">{{ loop.index }}. {{ u.name }} ({{ u.country }})</div>
        <div style="color: #fbbf24;">{{ u.money }} T</div>
    </div>
    {% endfor %}
</div>
"""

CHAT_HTML = """
<h2 style="color: #00d2ff; text-align: center;">💬 چت جهانی</h2>
<div class="chat-box" id="chat-box"></div>
<div style="display: flex; gap: 10px;">
    <input type="text" id="chat-input" placeholder="پیام..." style="margin: 0;" onkeypress="handleKeyPress(event)">
    <button onclick="sendMessage()" style="width: 80px; margin: 0; padding: 10px;">ارسال</button>
</div>

<script>
    let lastMessageCount = 0;
    function fetchMessages() {
        fetch('/api/chat').then(res => res.json()).then(data => {
            const chatBox = document.getElementById('chat-box');
            if (!chatBox) return;
            if (data.length !== lastMessageCount) {
                lastMessageCount = data.length;
                chatBox.innerHTML = '';
                data.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = 'chat-msg';
                    div.innerHTML = `<span class="chat-name">${msg.name}</span><span class="chat-text">${msg.text}</span>`;
                    chatBox.appendChild(div);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        });
    }
    function sendMessage() {
        const input = document.getElementById('chat-input');
        const text = input.value.trim();
        if(!text) return;
        fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: text})
        }).then(() => { input.value = ''; fetchMessages(); });
    }
    function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }
    setInterval(fetchMessages, 2000);
    fetchMessages();
</script>
"""

TRANSFER_HTML = """
<h2 style="color: #00d2ff; text-align: center;">💸 انتقال پول</h2>
<div class="card">
    {% if msg %}<div style="color: #22c55e; text-align: center; margin-bottom: 15px;">{{ msg }}</div>{% endif %}
    <form method="POST">
        <input type="text" name="target_id" placeholder="شناسه کاربر مقصد" required>
        <input type="number" name="amount" placeholder="مبلغ (تومان)" required>
        <button type="submit" class="btn-green">انتقال</button>
    </form>
</div>
"""

GIFT_HTML = """
<h2 style="color: #00d2ff; text-align: center;">🎁 کد هدیه</h2>
<div class="card">
    {% if msg %}<div style="color: #22c55e; text-align: center; margin-bottom: 15px;">{{ msg }}</div>{% endif %}
    <h3 style="color: #9ca3af; font-size: 14px;">مصرف کد</h3>
    <form method="POST" action="/gift">
        <input type="hidden" name="action" value="redeem">
        <input type="text" name="code" placeholder="کد را وارد کنید" required>
        <button type="submit" class="btn-green">مصرف</button>
    </form>
    <hr style="border-color: #1f2937; margin: 20px 0;">
    <h3 style="color: #9ca3af; font-size: 14px;">ساخت کد</h3>
    <form method="POST" action="/gift">
        <input type="hidden" name="action" value="create">
        <input type="number" name="amount" placeholder="مبلغ کد" required>
        <button type="submit">ساخت کد</button>
    </form>
</div>
"""

SECRET_HTML = """
<h2 style="color: #fbbf24; text-align: center;">🔑 دستورات ویژه</h2>
<div class="card">
    {% if msg %}<div style="color: #22c55e; text-align: center; margin-bottom: 15px;">{{ msg }}</div>{% endif %}
    <p style="color: #9ca3af; font-size: 13px; margin-bottom: 15px;">در این بخش می‌توانید کدهای ویژه خود را وارد کنید.</p>
    <form method="POST">
        <input type="text" name="code" placeholder="کد را وارد کنید" required>
        <button type="submit" class="btn-gold">ثبت کد</button>
    </form>
</div>
"""

SPY_HTML = """
<h2 style="color: #00d2ff; text-align: center;">🕵️‍♂️ جاسوسی</h2>
<div class="card">
    {% if msg %}<div style="color: #ef4444; text-align: center; margin-bottom: 15px;">{{ msg }}</div>{% endif %}
    <form method="POST">
        <input type="text" name="target_id" placeholder="شناسه دشمن" required>
        <button type="submit" class="btn-gold">جاسوسی (500 تومان)</button>
    </form>
    {% if target %}
    <div style="margin-top: 20px; background: #1f2937; padding: 15px; border-radius: 12px;">
        <div style="margin-bottom: 5px;">👤 <b>نام:</b> {{ target.name }}</div>
        <div style="margin-bottom: 5px;">💰 <b>پول:</b> {{ target.money }}</div>
        <div style="margin-bottom: 5px;">❤️ <b>جان:</b> {{ target.hp }}</div>
        <div style="margin-bottom: 5px;">⚡ <b>شیلد:</b> {{ target.shield_status }}</div>
        <div style="margin-bottom: 5px;">🛡 <b>پدافند زمینی:</b> {{ target.defense }} (HP: {{ target.defense_hp }})</div>
        <div>⚓ <b>پدافند دریایی:</b> {{ target.naval_defense_name }} (HP: {{ target.naval_defense_hp }})</div>
    </div>
    {% endif %}
</div>
"""

TASKS_HTML = """
<h2 style="color: #00d2ff; text-align: center;">📋 تسک‌های روزانه</h2>
<div class="card">
    {% for task in tasks %}
    <div class="shop-item" style="flex-direction: column; align-items: flex-start; gap: 10px;">
        <div style="font-weight: bold; color: #fff;">{{ task.name }}</div>
        <div style="font-size: 13px; color: #fbbf24;">جایزه: {{ task.reward }} تومان</div>
        
        {% set prog = p.get('daily_stats', {}).get(task.type, 0) %}
        <div style="width: 100%; background: #374151; border-radius: 5px; height: 10px; overflow: hidden;">
            {% set percent = (prog / task.target * 100) if prog < task.target else 100 %}
            <div style="width: {{ percent }}%; background: #00d2ff; height: 100%;"></div>
        </div>
        <div style="font-size: 12px; color: #9ca3af;">{{ prog }} / {{ task.target }}</div>

        {% if task.id in p.get('tasks_claimed', []) %}
            <button class="btn-green" disabled style="background: #333; color: #888; box-shadow: none;">دریافت شد ✓</button>
        {% elif prog >= task.target %}
            <form method="POST" action="/claim_task/{{ task.id }}" style="width: 100%;">
                <button type="submit" class="btn-green">دریافت جایزه</button>
            </form>
        {% else %}
            <button disabled style="background: #1f2937; color: #6b7280; box-shadow: none; border: 1px solid #374151;">انجام نشده</button>
        {% endif %}
    </div>
    {% endfor %}
</div>
"""

HELP_HTML = """
<h2 style="color: #00d2ff; text-align: center;">📖 راهنمای جامع بازی</h2>
<div class="card">
    <h3 class="help-title">🎯 هدف بازی</h3>
    <p class="help-text">با خرید سلاح به بازیکن‌های دیگه حمله کن، پولشون رو غارت کن و در صدر جدول قرار بگیر!</p>

    <h3 class="help-title">🛒 بازار سیاه</h3>
    <p class="help-text">هر روز ۳ آیتم خاص با تخفیف‌های ویژه (بین ۲۰ تا ۵۰ درصد) در این بخش قرار می‌گیرند. این آیتم‌ها فقط تا پایان روز در دسترس هستند.</p>

    <h3 class="help-title">🚀 موشک‌ها (حمله زمینی)</h3>
    <p class="help-text">
        - <span class="highlight">بالستیک (100 دمیج):</span> با پدافند ۱ به بالا دفع میشه.<br>
        - <span class="highlight">هایپرسونیک (150 دمیج):</span> با پدافند ۱ به بالا دفع میشه.<br>
        - <span class="highlight">کروز (250 دمیج):</span> با پدافند ۱ و ۲ دفع میشه.<br>
        - <span class="highlight">خوشه‌ای (400 دمیج):</span> با پدافند ۱ و ۲ دفع میشه.<br>
        - <span class="highlight">☢️ اتم (5000 دمیج):</span> فقط با سپر ماهواره‌ای (شانس ۲۰٪) دفع میشه!
    </p>

    <h3 class="help-title">✈️ جنگنده‌ها (حمله زمینی)</h3>
    <p class="help-text">
        - <span class="highlight">F-14 (1500 دمیج):</span> با پدافند ۳ به بالا دفع میشه.<br>
        - <span class="highlight">آپاچی (2000 دمیج):</span> با پدافند ۳ به بالا دفع میشه.<br>
        - <span class="highlight">Su-57 (3500 دمیج):</span> فقط با پدافند لیزری (۴) و ماهواره‌ای (۵) دفع میشه.<br>
        - <span class="highlight">B-2 (6000 دمیج):</span> بمب‌افکن سنگین. فقط با سپر ماهواره‌ای (۵) دفع میشه.
    </p>

    <h3 class="help-title">🪖 نیروی زمینی</h3>
    <p class="help-text">
        هیچ پدافند زمینی‌ای جلوی نیروی زمینی رو نمی‌گیره! (از پدافند رد میشه و مستقیم به جان می‌زنه)<br>
        - <span class="highlight">عادی (3000 دمیج)</span> | <span class="highlight">زره‌پوش (7000 دمیج)</span> | <span class="highlight">ویژه (12000 دمیج)</span>
    </p>

    <h3 class="help-title">🚢 ناوها (حمله دریایی)</h3>
    <p class="help-text">
        این سلاح‌ها اول با پدافند دریایی دشمن درگیر میشن.<br>
        - <span class="highlight">ناوشکن (4000 دمیج)</span> | <span class="highlight">زیردریایی (6000 دمیج)</span><br>
        - <span class="highlight">ناو هواپیمابر (8000 دمیج)</span> | <span class="highlight">ناو هسته‌ای (20000 دمیج)</span>
    </p>

    <h3 class="help-title">🛡 پدافند زمینی و دریایی</h3>
    <p class="help-text">
        - <span class="highlight">پدافند زمینی:</span> ۵ سطح داره (از پدافند ۱ تا سپر ماهواره‌ای). جلوی موشک‌ها و جنگنده‌ها رو می‌گیره.<br>
        - <span class="highlight">پدافند دریایی:</span> ۶ نوع داره (ناوچه گشتی، میدان مین، سونار، ساحلی، اسکورت، AEGIS). جلوی ناوهای دشمن رو می‌گیره.
    </p>

    <h3 class="help-title">🛢 نفت و ساختمون‌ها</h3>
    <p class="help-text">
        - با خرید <span class="highlight">تجهیزات نفت</span> در فروشگاه، به مرور زمان نفت تولید میشه.<br>
        - با دکمه <span class="highlight">فروش تمام نفت‌ها</span>، نفتت رو به پول تبدیل کن.<br>
        - <span class="highlight">پالایشگاه</span> قیمت فروش نفتت رو ۵۰٪ بیشتر می‌کنه.<br>
        - ماینر، کارخانه، مدرسه، آپارتمان و معدن طلا بهت درآمد پسیو (غیرفعال) میدن.
    </p>

    <h3 class="help-title">🏰 دژبند و کیت‌ها</h3>
    <p class="help-text">
        - <span class="highlight">دژبند:</span> حداکثر جان شما رو از ۱۰,۰۰۰ به ۱۵,۰۰۰ افزایش میده.<br>
        - <span class="highlight">کیت درمان:</span> ۱۰۰۰ واحد به جانت اضافه می‌کنه.<br>
        - <span class="highlight">کیت تعمیرات:</span> سلامتی پدافند زمینیت رو کاملاً پر می‌کنه.
    </p>

    <h3 class="help-title">🏛 مرکز فرماندهی و VIP</h3>
    <p class="help-text">
        - <span class="highlight">مرکز فرماندهی:</span> زمان کول‌داون حملات شما رو نصف می‌کنه و ایکس‌پی بیشتری بهت میده.<br>
        - <span class="highlight">VIP:</span> شیلد ۴۸ ساعته (دفع تمام حملات) + دوبرابر شدن درآمد ماینرها.
    </p>

    <h3 class="help-title">🎁 کد هدیه و انتقال پول</h3>
    <p class="help-text">
        - از منوی سه خط بالا می‌تونی پول به دوستات <span class="highlight">انتقال</span> بدی.<br>
        - می‌تونی با پولت <span class="highlight">کد هدیه</span> بسازی و دوستات اون رو توی بازی مصرف کنن.
    </p>
</div>
"""

@app.before_request
def check_login():
    if 'user_id' not in session and request.endpoint not in ['login', 'signup', 'static']:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        for uid, user in players_db.items():
            if user.get('name') == name and user.get('password') == password:
                session['user_id'] = uid
                return redirect(url_for('home'))
        return render_template_string(BASE_HTML, content=LOGIN_HTML.replace('ورود به حساب', 'ورود به حساب<br><small style="color:red;">نام کاربری یا رمز اشتباه است!</small>'))
    return render_template_string(BASE_HTML, content=LOGIN_HTML)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session: return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        country = request.form.get('country')
        password = request.form.get('password')
        
        if has_profanity(name) or has_profanity(country):
            error = "استفاده از کلمات رکیک مجاز نیست!"
        elif country not in VALID_COUNTRIES:
            error = "کشور وارد شده معتبر نیست!"
        else:
            for user in players_db.values():
                if user.get('name') == name:
                    error = "این نام کاربری قبلا گرفته شده است!"
                    break
            if not error:
                new_id = str(random.randint(1000, 9999))
                while new_id in players_db: new_id = str(random.randint(1000, 9999))
                players_db[new_id] = {
                    "name": name, "country": country, "password": password, "id": new_id,
                    "money": 5000, "hp": BASE_MAX_HP, "max_hp": BASE_MAX_HP,
                    "inv": {}, "miners": 0, "hospitals": 0, "oil": 0, "oil_level": 0,
                    "refineries": 0, "shield_until": 0, "last_daily": 0, "last_attack": 0,
                    "last_miner_check": time.time(), "buildings": {"factory": 0, "school": 0, "apartment": 0, "gold_mine": 0},
                    "defense": 0, "defense_hp": 0, "naval_defense": None, "naval_defense_hp": 0,
                    "level": 1, "xp": 0, "wins": 0, "losses": 0, "kills": 0, "damage": 0, "has_cmd": False,
                    "tasks": {}, "tasks_claimed": [], "stats_date": "", "daily_stats": {}
                }
                save_db(players_db, DB_FILE)
                session['user_id'] = new_id
                return redirect(url_for('home'))
    return render_template_string(BASE_HTML, content=render_template_string(SIGNUP_HTML, error=error))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    uid = session.get('user_id')
    if uid not in players_db: return redirect(url_for('logout'))
    p = players_db[uid]
    update_passive_income(p)
    get_player_stats(p)
    
    shield_until = p.get("shield_until", 0)
    now = time.time()
    if shield_until > now:
        rem = int(shield_until - now)
        p["shield_status"] = f"فعال ({format_shield_time(rem)})"
    else:
        p["shield_status"] = "غیرفعال"
    
    d_lvl = p.get("defense", 0)
    p["defense_name"] = SHOP_ITEMS.get(f"def_{d_lvl}", {}).get("name", "ندارد") if d_lvl > 0 else "ندارد"
    p["defense_hp"] = p.get("defense_hp", 0)
    
    nd_lvl = p.get("naval_defense")
    p["naval_defense_name"] = SHOP_ITEMS.get(nd_lvl, {}).get("name", "ندارد") if nd_lvl else "ندارد"
    p["naval_defense_hp"] = p.get("naval_defense_hp", 0)
    
    next_xp = 300 if p.get("level", 1) < 5 else 500
    
    return render_template_string(BASE_HTML, content=render_template_string(HOME_HTML, p=p, next_xp=next_xp, items=SHOP_ITEMS), p=p)

@app.route('/daily', methods=['GET', 'POST'])
def daily():
    p = players_db[session.get('user_id')]
    stats = get_player_stats(p)
    now = time.time()
    if now - p.get("last_daily", 0) >= 86400:
        b = p.get("buildings", {})
        income = DAILY_SALARY + (b.get('factory', 0) * 1500) + (b.get('school', 0) * 1000) + (b.get('apartment', 0) * 500) + (b.get('gold_mine', 0) * 2000)
        p["money"] += income
        p["last_daily"] = now
        stats['daily'] = stats.get('daily', 0) + 1
        save_db(players_db, DB_FILE)
    return redirect(url_for('home'))

@app.route('/sell_oil', methods=['GET', 'POST'])
def sell_oil():
    p = players_db[session.get('user_id')]
    stats = get_player_stats(p)
    oil = p.get("oil", 0)
    if oil > 0:
        price_per_barrel = 20 + (p.get("refineries", 0) * 10)
        p["money"] += oil * price_per_barrel
        p["oil"] = 0
        stats['sell_oil'] = stats.get('sell_oil', 0) + 1
        save_db(players_db, DB_FILE)
    return redirect(url_for('home'))

@app.route('/shop')
def shop():
    p = players_db[session.get('user_id')]
    black_market = get_black_market_items()
    return render_template_string(BASE_HTML, content=render_template_string(SHOP_HTML, p=p, items=SHOP_ITEMS, black_market=black_market), p=p)

def process_buy(p, item_key, price):
    if p['money'] >= price:
        p['money'] -= price
        stats = get_player_stats(p)
        stats['buys'] = stats.get('buys', 0) + 1
        stats['spent'] = stats.get('spent', 0) + price

        item = SHOP_ITEMS[item_key]
        msg = f"شما یک {item['name']} خریدید."
        
        if item_key == "miner": p["miners"] += 1
        elif item_key == "hospital": p["hospitals"] += 1
        elif item_key == "refinery": p["refineries"] += 1
        elif item_key.startswith("oil_kit_"): p["oil_level"] = int(item_key.split("_")[-1])
        elif item_key in ["factory", "school", "apartment", "gold_mine"]: p["buildings"][item_key] = p["buildings"].get(item_key, 0) + 1
        elif item_key == "vip":
            p["shield_until"] = time.time() + (48 * 3600)
            p['inv']['m_nuclear'] = p['inv'].get('m_nuclear', 0) + 2
            p['inv']['b2'] = p['inv'].get('b2', 0) + 1
        elif item_key == "cmd_center":
            if p.get("has_cmd"): 
                p['money'] += price
                return False, "شما قبلا مرکز فرماندهی دارید!"
            p["has_cmd"] = True
        elif item_key == "dozhband":
            p["max_hp"] = 15000
            p["hp"] = 15000
        elif item_key == "heal_kit":
            p["hp"] = min(p.get("max_hp", BASE_MAX_HP), p["hp"] + 1000)
        elif item_key == "repair_kit":
            if p.get("defense", 0) > 0:
                p["defense_hp"] = SHOP_ITEMS.get(f"def_{p['defense']}", {}).get("hp", 1000)
        elif item_key.startswith("shield_"):
            dur = int(item_key.split("_")[-1])
            hours = {1: 1, 2: 2, 3: 24}.get(dur, 1)
            p["shield_until"] = max(time.time(), p.get("shield_until", 0)) + (hours * 3600)
        elif item_key.startswith("def_"):
            lvl = int(item_key.split("_")[-1])
            if lvl > p.get("defense", 0):
                p["defense"] = lvl
                p["defense_hp"] = item["hp"]
            else:
                p['money'] += price
                return False, "شما پدافند زمینی بالاتری دارید!"
        elif item_key.startswith("nd_"):
            p["naval_defense"] = item_key
            p["naval_defense_hp"] = item["hp"]
        elif item_key.startswith("box_"):
            roll = random.random()
            if item_key == "box_epic":
                if roll < 0.35: p['inv']['m_ballistic'] = p['inv'].get('m_ballistic', 0) + 30; msg = "۳۰ بالستیک گرفتی!"
                elif roll < 0.70: p['inv']['m_hypersonic'] = p['inv'].get('m_hypersonic', 0) + 20; msg = "۲۰ هایپر گرفتی!"
                else: p['money'] += 4000; msg = "۴۰۰۰ تومان گرفتی!"
            elif item_key == "box_legendary":
                if roll < 0.35: p['inv']['m_hypersonic'] = p['inv'].get('m_hypersonic', 0) + 50; msg = "۵۰ هایپر گرفتی!"
                elif roll < 0.65: p['inv']['m_nuclear'] = p['inv'].get('m_nuclear', 0) + 1; msg = "۱ اتم گرفتی!"
                else: p['money'] += 8000; msg = "۸۰۰۰ تومان گرفتی!"
            elif item_key == "box_mythic":
                if roll < 0.35: p['inv']['m_nuclear'] = p['inv'].get('m_nuclear', 0) + 3; msg = "۳ اتم گرفتی!"
                elif roll < 0.65: p['inv']['m_ballistic'] = p['inv'].get('m_ballistic', 0) + 80; msg = "۸۰ بالستیک گرفتی!"
                else: p['money'] += 20000; msg = "۲۰۰۰۰ تومان گرفتی!"
        else:
            p['inv'][item_key] = p['inv'].get(item_key, 0) + 1
            
        save_db(players_db, DB_FILE)
        return True, msg
    return False, "پول کافی نداری!"

@app.route('/buy', methods=['POST'])
def buy():
    p = players_db[session.get('user_id')]
    data = request.json
    item_key = data.get('item')
    if item_key in SHOP_ITEMS:
        success, msg = process_buy(p, item_key, SHOP_ITEMS[item_key]['price'])
        return jsonify({"success": success, "msg": msg, "new_money": p['money']})
    return jsonify({"success": False, "msg": "آیتم یافت نشد.", "new_money": p['money']})

@app.route('/buy_black_market', methods=['POST'])
def buy_black_market():
    p = players_db[session.get('user_id')]
    data = request.json
    item_key = data.get('item')
    black_market = get_black_market_items()
    if item_key in black_market:
        success, msg = process_buy(p, item_key, black_market[item_key]['price'])
        return jsonify({"success": success, "msg": msg, "new_money": p['money']})
    return jsonify({"success": False, "msg": "آیتم یافت نشد.", "new_money": p['money']})

@app.route('/attack', methods=['GET', 'POST'])
def attack():
    uid = session.get('user_id')
    p = players_db[uid]
    msg = ""
    if request.method == 'POST':
        now = time.time()
        cd = 30 if p.get("has_cmd") else BASE_ATTACK_COOLDOWN
        
        if now - p.get("last_attack", 0) < cd:
            msg = f"کول‌داون! {int(cd - (now - p.get('last_attack', 0)))} ثانیه صبر کن."
        else:
            target_id = request.form.get('target_id')
            weapon = request.form.get('weapon')
            try: quantity = int(request.form.get('quantity', '1'))
            except: quantity = 1
                
            if quantity < 1: msg = "تعداد نامعتبر است!"
            elif target_id not in players_db: msg = "دشمن پیدا نشد!"
            elif target_id == uid: msg = "به خودت حمله نکن!"
            elif p['inv'].get(weapon, 0) < quantity: msg = f"شما به اندازه کافی {SHOP_ITEMS[weapon]['name']} ندارید! (موجودی: {p['inv'].get(weapon, 0)})"
            else:
                target = players_db[target_id]
                if target.get("shield_until", 0) > now:
                    p['inv'][weapon] -= quantity
                    msg = f"{target['name']} شیلد VIP داره! {quantity} عدد از سلاح شما هدر رفت."
                else:
                    total_dmg = SHOP_ITEMS[weapon]['dmg'] * quantity
                    p['inv'][weapon] -= quantity
                    p["last_attack"] = now
                    
                    stats = get_player_stats(p)
                    stats['attacks'] = stats.get('attacks', 0) + 1
                    
                    weapon_type = SHOP_ITEMS[weapon]['type']
                    blocked = False
                    
                    if weapon_type in ["missile", "fighter"]:
                        if target.get("defense", 0) > 0:
                            target["defense_hp"] -= total_dmg
                            if target["defense_hp"] <= 0:
                                target["defense"] = 0
                                target["defense_hp"] = 0
                                msg = f"🛡 با {quantity} شلیک، پدافند زمینی دشمن منهدم شد! ولی حمله مهار شد."
                            else:
                                msg = f"🛡 پدافند زمینی دشمن حمله را دفع کرد! (HP باقی‌مانده: {target['defense_hp']})"
                            blocked = True
                    elif weapon_type == "ship":
                        if target.get("naval_defense"):
                            target["naval_defense_hp"] -= total_dmg
                            if target["naval_defense_hp"] <= 0:
                                target["naval_defense"] = None
                                target["naval_defense_hp"] = 0
                                msg = f"🛡 با {quantity} شلیک، پدافند دریایی دشمن منهدم شد!"
                            else:
                                msg = f"⚓ پدافند دریایی دشمن حمله را دفع کرد! (HP باقی‌مانده: {target['naval_defense_hp']})"
                            blocked = True
                    
                    if not blocked:
                        target['hp'] -= total_dmg
                        p['damage'] = p.get('damage', 0) + total_dmg
                        
                        if target['hp'] <= 0:
                            loot = int(target['money'] * 0.5)
                            p['money'] += loot
                            target['money'] -= loot
                            target['hp'] = target.get("max_hp", BASE_MAX_HP)
                            p['wins'] = p.get('wins', 0) + 1
                            p['kills'] = p.get('kills', 0) + 1
                            stats['kills'] = stats.get('kills', 0) + 1
                            
                            xp_gain = 100
                            p['xp'] = p.get('xp', 0) + xp_gain
                            
                            while p.get('level', 1) < 10:
                                req_xp = 300 if p.get('level', 1) < 5 else 500
                                if p['xp'] >= req_xp:
                                    p['xp'] -= req_xp
                                    p['level'] = p.get('level', 1) + 1
                                else:
                                    break
                                    
                            msg = f"☠️ با {quantity} شلیک، دشمن ({target['name']}) نابود شد! {loot} تومان غارت کردی. (+{xp_gain} XP)"
                        else:
                            p['losses'] = p.get('losses', 0) + 1
                            msg = f"💥 {quantity} شلیک موفق! ({total_dmg} دمیج) جان دشمن ({target['name']}): {target['hp']}"
                            
                save_db(players_db, DB_FILE)

    user_weapons = []
    for w_key, count in p.get('inv', {}).items():
        if count > 0 and w_key in SHOP_ITEMS and SHOP_ITEMS[w_key].get('dmg', 0) > 0:
            user_weapons.append((w_key, f"{SHOP_ITEMS[w_key]['name']} ({count} عدد)"))

    return render_template_string(BASE_HTML, content=render_template_string(ATTACK_HTML, msg=msg, weapons=user_weapons, has_weapons=len(user_weapons)>0), p=p)

@app.route('/leaderboard')
def leaderboard():
    p = players_db[session.get('user_id')]
    top = sorted(players_db.values(), key=lambda x: x.get('money', 0), reverse=True)[:10]
    return render_template_string(BASE_HTML, content=render_template_string(LEADERBOARD_HTML, top=top), p=p)

@app.route('/help')
def help_page():
    p = players_db[session.get('user_id')]
    return render_template_string(BASE_HTML, content=HELP_HTML, p=p)

@app.route('/chat')
def chat_page():
    p = players_db[session.get('user_id')]
    return render_template_string(BASE_HTML, content=CHAT_HTML, p=p)

@app.route('/api/chat', methods=['GET', 'POST'])
def api_chat():
    global chat_db
    if request.method == 'POST':
        data = request.json
        text = escape(data.get('text', '').strip())
        if text:
            uid = session.get('user_id')
            user = players_db.get(uid)
            if user:
                chat_db.append({"name": user.get('name'), "text": text})
                chat_db = chat_db[-50:]
                save_db(chat_db, CHAT_FILE)
        return jsonify({"status": "ok"})
    return jsonify(chat_db)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    p = players_db[session.get('user_id')]
    msg = ""
    if request.method == 'POST':
        target_id = request.form.get('target_id')
        amount = int(request.form.get('amount', 0))
        if target_id in players_db and target_id != p['id']:
            if p['money'] >= amount and amount > 0:
                p['money'] -= amount
                players_db[target_id]['money'] += amount
                save_db(players_db, DB_FILE)
                msg = f"{amount} تومان به {players_db[target_id]['name']} منتقل شد."
            else: msg = "موجودی کافی نیست."
        else: msg = "شناسه مقصد نامعتبر است."
    return render_template_string(BASE_HTML, content=render_template_string(TRANSFER_HTML, msg=msg), p=p)

@app.route('/gift', methods=['GET', 'POST'])
def gift():
    global gift_db
    p = players_db[session.get('user_id')]
    msg = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'redeem':
            code = request.form.get('code').strip()
            if code in gift_db:
                amount = gift_db[code]
                p['money'] += amount
                del gift_db[code]
                save_db(gift_db, GIFT_FILE)
                save_db(players_db, DB_FILE)
                msg = f"کد مصرف شد! {amount} تومان دریافت کردید."
            else: msg = "کد نامعتبر است."
        elif action == 'create':
            amount = int(request.form.get('amount', 0))
            if p['money'] >= amount and amount >= 1000:
                p['money'] -= amount
                new_code = str(random.randint(10000000, 99999999))
                while new_code in gift_db: new_code = str(random.randint(10000000, 99999999))
                gift_db[new_code] = amount
                save_db(gift_db, GIFT_FILE)
                save_db(players_db, DB_FILE)
                msg = f"کد ساخته شد: {new_code}"
            else: msg = "موجودی کافی نیست یا مبلغ کمتر از ۱۰۰۰ است."
            
    return render_template_string(BASE_HTML, content=render_template_string(GIFT_HTML, msg=msg), p=p)

@app.route('/secret', methods=['GET', 'POST'])
def secret():
    p = players_db[session.get('user_id')]
    msg = ""
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if code.upper() == "KIANALIMADADI":
            if p.get("secret_used"):
                msg = "شما قبلا این کد را استفاده کرده‌اید!"
            else:
                p["money"] += 1000000
                p["secret_used"] = True
                save_db(players_db, DB_FILE)
                msg = "کد مخفی فعال شد! ۱,۰۰۰,۰۰۰ تومان دریافت کردید."
        elif code == "حقوق روزانه کیان علی مددی":
            p["money"] += 100000
            save_db(players_db, DB_FILE)
            msg = "دستور ویژه فعال شد! ۱۰۰,۰۰۰ تومان دریافت کردید."
        else:
            msg = "کد نامعتبر است."
            
    return render_template_string(BASE_HTML, content=render_template_string(SECRET_HTML, msg=msg), p=p)

@app.route('/spy', methods=['GET', 'POST'])
def spy():
    p = players_db[session.get('user_id')]
    msg = ""
    target = None
    if request.method == 'POST':
        target_id = request.form.get('target_id')
        if p['money'] >= 500:
            if target_id in players_db:
                p['money'] -= 500
                stats = get_player_stats(p)
                stats['spy'] = stats.get('spy', 0) + 1
                save_db(players_db, DB_FILE)
                t = players_db[target_id]
                
                t_shield = t.get("shield_until", 0)
                if t_shield > time.time():
                    rem = int(t_shield - time.time())
                    t["shield_status"] = f"دارد ({format_shield_time(rem)})"
                else:
                    t["shield_status"] = "ندارد"
                    
                nd_lvl = t.get("naval_defense")
                t["naval_defense_name"] = SHOP_ITEMS.get(nd_lvl, {}).get("name", "ندارد") if nd_lvl else "ندارد"
                target = t
            else:
                msg = "شناسه دشمن یافت نشد."
        else:
            msg = "پول کافی نداری! (هزینه جاسوسی ۵۰۰ تومان است)"
    return render_template_string(BASE_HTML, content=render_template_string(SPY_HTML, msg=msg, target=target), p=p)

@app.route('/tasks')
def tasks():
    p = players_db[session.get('user_id')]
    get_player_stats(p)
    daily_tasks = get_daily_tasks()
    return render_template_string(BASE_HTML, content=render_template_string(TASKS_HTML, p=p, tasks=daily_tasks), p=p)

@app.route('/claim_task/<task_id>', methods=['POST'])
def claim_task(task_id):
    p = players_db[session.get('user_id')]
    daily_tasks = get_daily_tasks()
    
    task = next((t for t in daily_tasks if t['id'] == task_id), None)
    if task:
        stats = get_player_stats(p)
        prog = stats.get(task['type'], 0)
        
        if prog >= task['target'] and task_id not in p.get('tasks_claimed', []):
            p['tasks_claimed'].append(task_id)
            p['money'] += task['reward']
            save_db(players_db, DB_FILE)
            
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
