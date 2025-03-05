from flask import Flask
from pywebio.platform.flask import webio_view
from pywebio.input import input, select, checkbox, actions
from pywebio.output import put_text, put_table, put_markdown, put_image, put_loading, clear, put_html
import time
import os
import json

app = Flask(__name__)

# ملف تخزين بيانات المستخدمين
USER_DB_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_DB_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

users_db = load_users()

# قائمة الطعام مع الأسعار والصور
menu = {
    "🍔 برجر": {"price": 50, "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQU_bM1lCxUdA_RKq9-ZXgjboh8tLyS3pf3nw&s"},
    "🌭 هوت دوج": {"price": 30, "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbHsfulMU68l1j-BFwOvL9DBD1wdt6dQ87PA&s"},
    "🍕 بيتزا": {"price": 80, "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMwYJrDDJyoylgImVurbSNe-JLgzjNlZE5EQ&s"},
    "🍟 بطاطس": {"price": 25, "image": ""},
    "🥤 مشروب غازي": {"price": 15, "image": ""}
}

# شاشة التحميل المتحركة مع شعار العقرب المتوهج
loading_animation = """
<style>
body {
    background-color: black;
    color: #FFD700;
    font-family: monospace;
    text-align: center;
    overflow-y: auto;
    margin: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

@keyframes glow {
  0% { filter: drop-shadow(0 0 10px cyan); }
  50% { filter: drop-shadow(0 0 40px blue); }
  100% { filter: drop-shadow(0 0 10px cyan); }
}

.scorpion-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 50vh;
    width: 100%;
}

.scorpion-logo {
    width: 300px;
    height: 300px;
    animation: glow 2s infinite alternate;
}
</style>
<div class='scorpion-container'>
    <img class='scorpion-logo' src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQO8pxGq2zzyd07e1TI9oJ3iRpnqB_mi2ORbc0DtuUxLbWao_rSbokDTPLX3_Oy-oV7u_M&usqp=CAU' width='300' height='300'>
</div>
<h2>🖥️ نظام الطلبات المتقدم</h2>
<p>جارٍ التحميل...</p>
"""

def animated_startup():
    put_html(loading_animation)
    put_loading()
    time.sleep(3)
    clear()
    auth_menu()

def auth_menu():
    put_html(loading_animation)
    choice = actions("🔑 اختر خيارًا:", [
        {"label": "🆕 تسجيل حساب جديد", "value": "register"},
        {"label": "🔐 تسجيل الدخول", "value": "login"}
    ])
    if choice == "register":
        register()
    else:
        login()

def register():
    put_html(loading_animation)
    put_markdown("# 🆕 تسجيل حساب جديد")
    username = input("👤 اسم المستخدم:")
    email = input("📧 البريد الإلكتروني:")
    password = input("🔒 كلمة المرور:", type="password")
    
    if username in users_db:
        put_text("❌ اسم المستخدم مسجل بالفعل!")
        return register()
    
    users_db[username] = {"password": password, "email": email}
    save_users(users_db)
    put_text("✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
    login()

def login():
    put_html(loading_animation)
    put_markdown("# 🔑 تسجيل الدخول")
    username = input("👤 اسم المستخدم:")
    password = input("🔒 كلمة المرور:", type="password")
    
    if username in users_db and users_db[username]["password"] == password:
        put_text(f"✅ مرحبًا {username}، تم تسجيل الدخول بنجاح!")
        order_food()
    else:
        put_text("❌ اسم المستخدم أو كلمة المرور غير صحيحة!")
        login()

def order_food():
    put_html(loading_animation)
    put_markdown("# 🍽️ مرحبًا في مطعم الأكلات السريعة")
    phone = input("📞 أدخل رقم هاتفك:")
    selected_items = checkbox("📋 اختر وجباتك:", list(menu.keys()))
    
    if not selected_items:
        put_text("❌ يجب اختيار صنف واحد على الأقل!")
        return

    put_markdown("## 🍽️ صور الأطعمة التي اخترتها:")
    for item in selected_items:
        put_markdown(f"### {item}")
        put_image(menu[item]["image"])

    address = input("📍 أدخل عنوان التوصيل:")
    payment_method = select("💳 اختر وسيلة الدفع:", ["كاش عند الاستلام", "بطاقة إلكترونية"])
    total_price = sum(menu[item]['price'] for item in selected_items)

    put_markdown("## ✅ ملخص طلبك:")
    put_table([
        ["رقم الهاتف", phone],
        ["العنوان", address],
        ["وسيلة الدفع", payment_method],
        ["الأصناف المختارة", ", ".join(selected_items)],
        ["💰 السعر الإجمالي", f"{total_price} جنيه"]
    ])
    
    put_text("✅ تم إرسال طلبك بنجاح!")
    put_text("📩 سيتم التواصل معك قريبًا لتأكيد الطلب.")

app.add_url_rule("/", "webio", webio_view(animated_startup), methods=["GET", "POST"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
