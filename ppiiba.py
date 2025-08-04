import asyncio
import random
import time
import os
import json
from telethon import TelegramClient, events, Button
from gtts import gTTS

api_id = 23656695
api_hash = 'fd1f248529524dde45cb918affe78982'
MY_USER_ID = 7341413250  # Твій user_id

client = TelegramClient('ppiiba', api_id, api_hash)

start_time = time.time()
command_counter = 0

quotes = [
    "Вір у себе і все стане можливим.",
    "Не бійся помилок — вони крок до успіху.",
    "Кожен день — нова можливість.",
    "Роби сьогодні те, що інші не хочуть, завтра будеш мати те, що інші не можуть.",
    "Успіх — це результат маленьких зусиль, повторених щодня."
]

# --- Лічильник повідомлень з постійним збереженням ---
MSG_FILE = "msg_counter.json"
if os.path.exists(MSG_FILE):
    with open(MSG_FILE, "r") as f:
        chat_counters = json.load(f)
else:
    chat_counters = {}

def save_counters():
    with open(MSG_FILE, "w") as f:
        json.dump(chat_counters, f)

def increment_counter():
    global command_counter
    command_counter += 1

def is_me(event):
    return event.sender_id == MY_USER_ID

# --- Рахуємо всі повідомлення ---
@client.on(events.NewMessage)
async def count_messages(event):
    chat_id = str(event.chat_id)
    chat_counters[chat_id] = chat_counters.get(chat_id, 0) + 1
    save_counters()

# --- Команда для перевірки кількості повідомлень ---
@client.on(events.NewMessage(pattern=r'/msgcount'))
async def msg_count(event):
    if not is_me(event):
        return
    chat_id = str(event.chat_id)
    count = chat_counters.get(chat_id, 0)
    await event.reply(f"У цьому чаті бот нарахував {count} повідомлень 📊")
    await event.delete()

# --- Основні команди ---
@client.on(events.NewMessage(pattern=r'/quote'))
async def send_quote(event):
    if not is_me(event):
        return
    increment_counter()
    await event.reply(random.choice(quotes))
    await event.delete()

@client.on(events.NewMessage(pattern=r'/ping'))
async def pong(event):
    if not is_me(event):
        return
    increment_counter()
    await event.reply('Pong!')
    await event.delete()

@client.on(events.NewMessage(pattern=r'/info'))
async def info(event):
    if not is_me(event):
        return
    increment_counter()
    await event.reply('Це твій крутий юзербот! 👑')
    await asyncio.sleep(2)
    await event.delete()

@client.on(events.NewMessage(pattern=r'/h'))
async def help_cmd(event):
    if not is_me(event):
        return
    increment_counter()
    help_text = (
        "/myt @нік хвилини - блокування\n"
        "/sk 1-3 - змінити шрифт\n"
        "/spavn кількість текст - спам\n"
        "/ping - перевірка\n"
        "/info - інформація\n"
        "/rainbow - веселка\n"
        "/quote - мотиваційна цитата\n"
        "/voice [текст] - озвучка тексту\n"
        "/stats - статистика бота\n"
        "/msgcount - кількість повідомлень у чаті\n"
        "/h - допомога\n"
        "/getid - твій user_id\n"
        "/tictactoe [@нік] - гра Хрестики-Нолики"
    )
    await event.reply(help_text)
    await event.delete()

@client.on(events.NewMessage(pattern=r'/voice (.+)'))
async def voice_message(event):
    if not is_me(event):
        return
    increment_counter()
    text = event.pattern_match.group(1)
    tts = gTTS(text=text, lang='uk')
    filename = "voice.mp3"
    tts.save(filename)
    await client.send_file(event.chat_id, filename, voice_note=True)
    os.remove(filename)
    await event.delete()

@client.on(events.NewMessage(pattern=r'/stats'))
async def stats(event):
    if not is_me(event):
        return
    increment_counter()
    uptime = time.time() - start_time
    uptime_str = f"{int(uptime // 3600)} год {(int(uptime) % 3600) // 60} хв"
    text = f"Команд виконано: {command_counter}\nЧас роботи: {uptime_str}"
    await event.reply(text)
    await event.delete()

@client.on(events.NewMessage(pattern=r'/getid'))
async def get_my_id(event):
    await event.reply(f"Твій user_id: {event.sender_id}")

# --- Гра "Хрестики-Нолики" ---
active_games = {}

def new_game(player1_id, player2_id):
    return {
        "board": [" "]*9,
        "turn": player1_id,
        "players": [player1_id, player2_id],
        "symbols": {player1_id: "❌", player2_id: "⭕"},
        "moves": 0
    }

def render_board(board):
    rows = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = board[i+j]
            text = cell if cell != " " else "▫️"
            row.append(Button.inline(text, data=str(i+j)))
        rows.append(row)
    return rows

def check_win(board, symbol):
    win_positions = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    return any(all(board[i] == symbol for i in pos) for pos in win_positions)

@client.on(events.NewMessage(pattern=r'/tictactoe(?:\s+@(\w+))?'))
async def tictactoe_start(event):
    if not is_me(event):
        return
    player1 = event.sender_id
    username = event.pattern_match.group(1)
    if username:
        try:
            entity = await client.get_entity(username)
            player2 = entity.id
        except:
            await event.reply("Користувача не знайдено.")
            return
    else:
        player2 = player1

    game = new_game(player1, player2)
    active_games[event.chat_id] = game
    board_buttons = render_board(game["board"])
    await event.reply(f"Гра Хрестики-Нолики почалася!\nХід: {game['symbols'][game['turn']]}", buttons=board_buttons)
    await event.delete()

@client.on(events.CallbackQuery)
async def callback_handler(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    if chat_id not in active_games:
        await event.answer("Гра не активна.")
        return
    game = active_games[chat_id]
    if user_id != game["turn"]:
        await event.answer("Зараз не твій хід!")
        return
    pos = int(event.data.decode('utf-8'))
    if game["board"][pos] != " ":
        await event.answer("Ця клітинка вже зайнята.")
        return
    symbol = game["symbols"][user_id]
    game["board"][pos] = symbol
    game["moves"] += 1

    if check_win(game["board"], symbol):
        board_buttons = render_board(game["board"])
        await event.edit(f"Гравець {symbol} переміг! 🎉", buttons=board_buttons)
        del active_games[chat_id]
        return
    elif game["moves"] == 9:
        board_buttons = render_board(game["board"])
        await event.edit("Нічия! 🤝", buttons=board_buttons)
        del active_games[chat_id]
        return

    game["turn"] = game["players"][0] if game["turn"] == game["players"][1] else game["players"][1]
    board_buttons = render_board(game["board"])
    await event.edit(f"Хід: {game['symbols'][game['turn']]}", buttons=board_buttons)
    await event.answer()

# --- Запуск ---
async def main():
    await client.start()
    print("Бот запущено...")
    await client.run_until_disconnected()

asyncio.run(main())
