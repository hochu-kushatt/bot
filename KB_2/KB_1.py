import telebot
from telebot import types
import json
from pycbrf.toolbox import ExchangeRates # импортируем библиотеку


bot = telebot.TeleBot('token');

list_of_users = {}
my_chats = [1022066349]
kurs_trig = 0

# list_of_aktiviti = []
# list_of_titles = []

def reading_my_chats():
    with open('chats.txt', 'r') as filehandle:
        places = [int(current_place.rstrip()) for current_place in filehandle.readlines()]
    return places

def write_my_chats():
    with open('chats.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % place for place in my_chats)
    return print('list saved')
        
def parse_keys_to_int(initial_value):# считать ключи
    if isinstance(initial_value, dict):
        return {int(key):value for key,value in initial_value.items()}
    return initial_value

my_chats = reading_my_chats()

try:
    with open('data.json', 'r') as f:
        print('new file')
        list_of_users = json.load(f, object_hook=parse_keys_to_int)
        bot.send_message(1022066349, "бот был перезагружен")
        bot.send_message(1022066349, "резервная копия рейтинга подгружена")
        # list_of_users = list_of_users.items()
        
except Exception:
    pass

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("❓ Помощь")
    btn2 = types.KeyboardButton("👋 Мой уровень")
    btn3 = types.KeyboardButton("💪 Топ активности")
    btn4 = types.KeyboardButton("📈 Что по рублю?")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Привет)", reply_markup=markup)
        
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global kurs_trig
    if message.from_user.id == 1022066349:
        if message.text[0 : 4] == '/add':
            my_chats.append(int(message.text[5:]))
            bot.send_message(1022066349, "added!")
            # write_my_chats()
    if (message.chat.id in my_chats):
        global list_of_users
        global start
        
        def sorted_tuple(): # сортирует челиков по колву сообщений с помощью лямбдафункции
            sort_tuple = sorted(list_of_users.items(), key=lambda x: x[1], reverse=True)
            sort_tuple = list(map(list, sort_tuple))
            return sort_tuple
        
        # bot.send_message(message.chat.id, message.chat.id)
        list_of_users[message.from_user.id] = list_of_users.get(message.from_user.id, 0) + 1
        if message.text == "❓ Помощь":
            bot.send_message(message.chat.id, "Привет, вот, что я могу:")
            bot.send_message(message.chat.id, "==> Покажу рейтинг самых активных пользователей чата")
            bot.send_message(message.chat.id, "==> Покажу рейтинг одного пользователя")
            bot.send_message(message.chat.id, "==> Покажу курс рубля к доллару и евро \nпо состоянию на любой день ")
            sticker = open('sticker.webp', 'rb')
            bot.send_photo(message.chat.id, sticker)
        if message.text == "👋 Мой уровень":
            try:
                sort_list = sorted_tuple()
                place_in_slist = 1 + sort_list.index([message.from_user.id, list_of_users[message.from_user.id]])
                bot.send_message(message.chat.id, f"Вы написали {list_of_users[message.from_user.id]} сообщений")
                bot.send_message(message.chat.id, f"Ваша позиция в рейтинге - {place_in_slist}")

            except Exception as ex:
                bot.send_message(message.chat.id, ex)
                #bot.send_message(message.chat.id, ex)
        if message.text == "💪 Топ активности":
            trig = 1
            sorted_list = sorted_tuple()
            for i in range(len(sorted_list)):# переюор челиков для просвоения юзернеймом
                user_id = sorted_list[i][0]
                sorted_list[i][0] = bot.get_chat_member(user_id, user_id).user.username
            for line in sorted_list:
                if trig <= 10:
                    string = f"@{line[0]} послал {str(line[1])} сообщений"
                    bot.send_message(message.chat.id, f"{trig}-е место ==> {string}")
                else:
                    break
                trig += 1
            bot.send_message(message.chat.id, "Первые десять мест по активности")
        if message.text == "📈 Что по рублю?":
            bot.send_message(message.chat.id, "Введите дату в формате \nгггг-мм-дд")
           
            kurs_trig = 1
        
        if  (len(message.text) == 10) and (kurs_trig == 1):
            try:
                data = message.text
                rates = ExchangeRates(data) # задаем дату, за которую хотим получить данные
                result = [rates['USD'].value, rates['EUR'].value]
                bot.send_message(message.chat.id, f"{data}")
                bot.send_message(message.chat.id, f"RU-USD: {result[0]}")
                bot.send_message(message.chat.id, f"RU-EUR: {result[1]}")
                img = open('rubl.jpg', 'rb')
                bot.send_photo(message.chat.id, img)
            except Exception as ex:
                bot.send_message(message.chat.id, "Формат даты неверен(((")
                data = None
                rates = ExchangeRates(data)
                result = [rates['USD'].value, rates['EUR'].value]
                if data == None:
                    data = 'сегодня'
                bot.send_message(message.chat.id, f"{data}")
                bot.send_message(message.chat.id, f"RU-USD: {result[0]}")
                bot.send_message(message.chat.id, f"RU-EUR: {result[1]}")
                img = open('rubl.jpg', 'rb')
                bot.send_photo(message.chat.id, img)
            kurs_trig = 0
                
        
        with open('data.json', 'w') as f:
            json.dump(list_of_users, f)
    else:
        bot.send_message(1022066349, "НСД к боту")
        user_id = message.from_user.id
        bot.send_message(1022066349, f"{message.chat.id}, @{bot.get_chat_member(user_id, user_id).user.username}")
        
bot.polling(non_stop=True, interval=0)