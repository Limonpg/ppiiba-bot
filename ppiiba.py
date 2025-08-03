import asyncio
import time
from datetime import datetime
from telethon import TelegramClient, events

api_id = 23656695
api_hash = 'fd1f248529524dde45cb918affe78982'
session_name = "ppiiba"

current_heart = [
    "🤍🤍🤍🤍🤍🤍🤍🤍🤍",
    "🤍🤍❤️❤️🤍❤️❤️🤍🤍",
    "🤍❤️❤️❤️❤️❤️❤️❤️🤍",
    "🤍❤️❤️❤️❤️❤️❤️❤️🤍",
    "🤍❤️❤️❤️❤️❤️❤️❤️🤍",
    "🤍🤍❤️❤️❤️❤️❤️🤍🤍",
    "🤍🤍🤍❤️❤️❤️🤍🤍🤍",
    "🤍🤍🤍🤍❤️🤍🤍🤍🤍",
    "🤍🤍🤍🤍🤍🤍🤍🤍🤍"
]

colors = {
    "red": "❤️",
    "blue": "💙",
    "green": "💚",
    "yellow": "💛",
    "purple": "💜",
    "black": "🖤"
}

banned_users = {}  # {user_id: unban_timestamp or 0 for forever}
current_font = 1   # 1 = normal, 2 = bold, 3 = fancy

client = TelegramClient(session_name, api_id, api_hash)

async def temp_respond(event, text, delay=5):
    msg = await event.respond(text)
    await asyncio.sleep(delay)
    await msg.delete()

# ====== Шрифти з підтримкою кирилиці ======
def apply_font(text: str) -> str:
    global current_font
    if current_font == 1:
        return text

    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789"
    bold =   "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭" \
             "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇" \
             "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" \
             "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" \
             "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟟𝟴𝟵"
    fancy =  "𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵" \
             "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏" \
             "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" \
             "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" \
             "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"

    if current_font == 2:
        trans = str.maketrans(normal, bold)
    elif current_font == 3:
        trans = str.maketrans(normal, fancy)
    else:
        return text

    return text.translate(trans)

# ====== Сердечко ======
@client.on(events.NewMessage(pattern=r'^/heart$'))
async def send_heart(event):
    await event.delete()
    styled_heart = [apply_font(row) for row in current_heart]
    await event.respond("\n".join(styled_heart))

# ====== Зміна кольору ======
@client.on(events.NewMessage(pattern=r'^/color (.+)$'))
async def change_color(event):
    await event.delete()
    color_name = event.pattern_match.group(1).lower()
    if color_name not in colors:
        await temp_respond(event, "Доступні кольори: " + ", ".join(colors.keys()))
        return

    new_color = colors[color_name]
    global current_heart
    current_heart = [row.replace("❤️", new_color) for row in current_heart]
    await temp_respond(event, f"Колір змінено на {new_color}! Напиши /heart щоб побачити нове сердечко.")

# ====== Зміна шрифту ======
@client.on(events.NewMessage(pattern=r'^/sk (\d+)$'))
async def change_font(event):
    await event.delete()
    global current_font
    choice = int(event.pattern_match.group(1))
    if choice not in [1, 2, 3]:
        await temp_respond(event, "Вибери шрифт 1, 2 або 3.")
        return
    current_font = choice
    await temp_respond(event, f"✅ Шрифт змінено на стиль {choice}. Напиши /heart щоб побачити результат.")

# ====== Блокування ======
@client.on(events.NewMessage(pattern=r'^/myt (@\w+)(?: (\d+))?$'))
async def mute_user(event):
    await event.delete()
    chat = await event.get_chat()
    username = event.pattern_match.group(1)
    duration = event.pattern_match.group(2)
    user = await client.get_entity(username)

    if duration:
        duration = int(duration)
        banned_users[user.id] = time.time() + duration * 60
        mute_until = time.time() + duration * 60
        await client.edit_permissions(
            chat.id, user.id,
            send_messages=False,
            until_date=mute_until
        )
        await temp_respond(event, f"🔇 {username} заблокований на {duration} хв.")
    else:
        banned_users[user.id] = 0
        await client.edit_permissions(chat.id, user.id, send_messages=False)
        await temp_respond(event, f"🔇 {username} заблокований назавжди.")

# ====== Розбан ======
@client.on(events.NewMessage(pattern=r'^/unmyt (@\w+)$'))
async def unmute_user(event):
    await event.delete()
    chat = await event.get_chat()
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    if user.id in banned_users:
        banned_users.pop(user.id)
        await client.edit_permissions(chat.id, user.id, send_messages=True)
        await temp_respond(event, f"✅ {username} розблокований.")
    else:
        await temp_respond(event, f"ℹ️ {username} не був у бані.")

# ====== Допомога ======
@client.on(events.NewMessage(pattern=r'^/h$'))
async def help_command(event):
    await event.delete()
    commands = [
        "/heart – показати сердечко",
        "/color <колір> – змінити колір сердечка",
        "/sk <1-3> – змінити шрифт сердечка",
        "/myt @username [хвилини] – заблокувати користувача",
        "/unmyt @username – розблокувати користувача",
        "/spavn <кількість> <текст> – спам обраним текстом",
        "/ping – перевірка бота",
        "/info @username – інформація про користувача",
        "/rainbow – райдужне сердечко",
        "/h – показати всі команди"
    ]
    await temp_respond(event, "📜 Список команд:\n" + "\n".join(commands))

# ====== Спам ======
@client.on(events.NewMessage(pattern=r'^/spavn (\d+) (.+)$'))
async def spavn(event):
    await event.delete()
    count = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)

    if count > 200:
        await temp_respond(event, "⚠️ Максимум 200 повідомлень за раз!")
        return

    styled_text = apply_font(text)
    for i in range(count):
        await event.respond(styled_text)
        await asyncio.sleep(0.2)  # антиспам

# ====== Ping ======
@client.on(events.NewMessage(pattern=r'^/ping$'))
async def ping(event):
    start = time.time()
    await event.delete()
    msg = await event.respond("🏓 Пінг...")
    end = time.time()
    latency = int((end - start) * 1000)
    await msg.edit(f"🏓 Пінг: {latency} ms")
    await asyncio.sleep(5)
    await msg.delete()

# ====== Info ======
@client.on(events.NewMessage(pattern=r'^/info (@\w+)$'))
async def user_info(event):
    await event.delete()  # видаляємо тільки команду
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    
    info_text = (
        f"👤 Інформація про користувача:\n"
        f"• Ім'я: {user.first_name or '-'}\n"
        f"• Прізвище: {user.last_name or '-'}\n"
        f"• Юзернейм: @{user.username}\n"
        f"• ID: {user.id}\n"
        f"• Дата реєстрації: {user.date.strftime('%d.%m.%Y') if user.date else '-'}"
    )
    
    await event.respond(info_text)

# ====== Rainbow ======
@client.on(events.NewMessage(pattern=r'^/rainbow$'))
async def rainbow(event):
    await event.delete()
    rainbow_colors = ["❤️","🧡","💛","💚","💙","💜"]
    msg = None
    
    for color in rainbow_colors * 2:  # 2 кола
        rainbow_heart = "\n".join(
            row.replace("❤️", color) for row in current_heart
        )
        styled_heart = [apply_font(row) for row in rainbow_heart.split("\n")]
        
        if msg is None:
            msg = await event.respond("\n".join(styled_heart))
        else:
            await msg.edit("\n".join(styled_heart))
        await asyncio.sleep(0.7)

# ====== Автоблок ======
@client.on(events.NewMessage)
async def block_messages(event):
    chat = await event.get_chat()
    user_id = event.sender_id

    if user_id in banned_users:
        unban_time = banned_users[user_id]
        if unban_time == 0 or time.time() < unban_time:
            await event.delete()
        else:
            banned_users.pop(user_id, None)
            await client.edit_permissions(chat.id, user_id, send_messages=True)
            await temp_respond(event, f"✅ Користувач {user_id} автоматично розблокований.")

print("Юзербот запущений!")

async def main():
    await client.start()
    print("Авторизація успішна! Слухаю команди...")
    await client.run_until_disconnected()

asyncio.run(main())
