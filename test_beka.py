import telebot
import json
from telebot import types 
import time 
import random
from file_utils import get_file_json

import dotenv
import os

dotenv.load_dotenv()

TELEGRAM_BOT_KEY = os.getenv("TELEGRAM_BOT_KEY", None)
if TELEGRAM_BOT_KEY == None:
    raise(
        EnvironmentError(
            "environment variable TELEGRAM_BOT_KEY is not set!\n" +
            "create a .env file if developing in local"
        )
    )


bot = telebot.TeleBot(TELEGRAM_BOT_KEY)
_data = get_file_json("data.json")
mapping = {}
_all_data =   {
    "start": {
        "text": "Привет! 👀\nВы можете пойти к терапевту, а можете ставить себе диагнозы сами с помощью телеграмм-ботов, созданных непрофессионалами!",
        "reply": ["Ставить себе диагноз 🥸", "Обратиться к психотерапевту 🌚"]
    },

    "explanation":{
        "text":
"""*Внимательно прочтите группы утверждений, которые будут ниже🧐*
В каждой из них отметьте тот пункт, который наиболее полно отражает ваше состояние в последние *две недели*, включая сегодняшний день.
Если в какой-то из групп вам сложно определиться между двумя-тремя вариантами, выбирайте более печальный!
Вы готовы?""",
        "reply": ["ПРОДОЛЖИТЬ"],
        "photo": 'have_a_drink.jpeg'
    }, 

    "fack_you": {
        "text": "Ну и  иди нахуй!"
        }, 

    "main_part": {
        "reply": [
                ["Отлично! 💅", "Йоу-йоу, круто!", "Неплохо! 🤔", "У тебя не все потеряно!"],
                ["Оу 😦", "Не повезло тебе!", "Слегка прескорбно 🤧", "У тебя сложная ситуация"],
                ["Удивляешь!", "Печально 😓", "Ты конечно даешь 😱", "Жуть 🫢" ],
                ["О ужас! 😖", "Врагу не пожелаешь! 😟", "Твоя жизнь - к деньгам психологу 💸", "Жаль этого добряка 😬"],
                ["С этим явный дисбаланс 😳", "Тут знать бы норму!😬", "Перебор! 🫣", "Не маловато? 😬"]
                ],
        "smiles": ['😃', '😳', '😞', '😫']
        },

    "results":{
        "smiles": ['😋', '😒', '😖', '😭'],
        "reply": [
                "У вас нет депрессии, не тратьте время на ипохондрию! (0–13)",
                "Вероятна лёгкая депрессия (субдепрессия) 14–19 ",
                "Вероятна умеренная депрессия! Пора пить таблетки (20–28)",
                "Зовите на помощь, у вас тяжёлая депрессия. Состояние тем сложнее, чем больше количество баллов (29–63)"
                ], 

    }
    }



def init_user(message):
    chat_id = message.chat.id
    start_id = message.id

    user = {
        "key": 1,
        "result": 0,
        "start_id": start_id,
        "flag_start": False
    }

    if f"{chat_id}" in mapping and "start_id" in mapping[f"{chat_id}"]:
        user["start_id"] = mapping[f"{chat_id}"]["start_id"]
    
    mapping[f"{chat_id}"] = user


def start_markup():
    reply = _all_data["start"]["reply"]
    markup = types.InlineKeyboardMarkup()
    mar1 = types.InlineKeyboardButton(reply[0], callback_data="explanation")
    mar2 = types.InlineKeyboardButton(reply[1], callback_data="fuck_you")
    markup.add(mar1, mar2, row_width=1)
    return markup

def explanation_markup(explanation_data):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(explanation_data['reply'][0], callback_data="first_question"))
    return markup

def delete_mess_fuck_u(message):
    global mapping
    chat_id = message.chat.id
    message_id = message.id
    start_id = mapping[f"{chat_id}"].get("start_id")

    i = 0
    while message_id - i != start_id:
        bot.delete_message(chat_id, message_id - i)
        i += 1

    bot.delete_message(chat_id, start_id)
    if mapping[f"{chat_id}"].get("start_id") != None:
        del mapping[f"{chat_id}"]["start_id"]

def send_reply_main(chat_id, key, command):
    var_answers = _all_data["main_part"]["reply"]
    which_list = command if key not in [15, 20] else 4

    bot.send_message(chat_id, var_answers[which_list][random.randint(0, 3)])


@bot.message_handler(commands= ['start'])
def reply_to_start(message):
    text = _all_data["start"]['text']
    init_user(message)
    markup = start_markup()
    

    bot.send_message(message.chat.id, text, reply_markup=markup)



@bot.callback_query_handler(func= lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    global mapping
    key = mapping[f"{chat_id}"]["key"]




    if call.data == "explanation":
        explanation_data = _all_data["explanation"]
        markup = explanation_markup(explanation_data)
        

        photo = explanation_data["photo"]
        text = explanation_data["text"]
        
        bot.send_photo(chat_id,  photo=open(photo, 'rb'))
        time.sleep(1)
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        
        


    elif call.data == "fuck_you":
        chat_id = call.message.chat.id
        text = _all_data["fack_you"]["text"]
        
        delete_mess_fuck_u(call.message)

        bot.send_message(chat_id, text)

    elif call.data == "first_question":
        flag = mapping[f"{chat_id}"]["flag_start"]
        if flag == False:
            mapping[f"{chat_id}"]["flag_start"] = True
            bot.send_message(chat_id, "Приступаем!")
            send_next_quest_main(call.message, 1)
        
    else:
        calldata = json.loads(call.data)
        num_quest = int(calldata["num_quest"])
        command = int(calldata["command"])

        if num_quest == key:
            if  num_quest < 21:

                
                send_reply_main(chat_id, key, command)
                send_next_quest_main(call.message, (num_quest + 1))

                mapping[f"{chat_id}"]["result"] += command
                mapping[f"{chat_id}"]["key"] += 1
            else: 
                mapping[f"{chat_id}"]["result"] += command
                send_results(chat_id)


def send_next_quest_main(message, num_quest):
    chat_id = message.chat.id

    markup = make_markup(num_quest)
    message_ = make_message(num_quest)

    time.sleep(1)
    bot.send_message(chat_id, f"{message_}", reply_markup=markup, parse_mode="Markdown")



def make_markup(num_quest):
    markup = types.InlineKeyboardMarkup()
    buttons = []

    for i in range(1, 5)  :
        make_btn = types.InlineKeyboardButton
        smiles = _all_data["main_part"]["smiles"]

        calldata_json = json.dumps({"num_quest": f'{num_quest}', "command": f'{i - 1}' })
        buttons.append(make_btn(f'{i}{smiles[i - 1]}', callback_data = calldata_json))
    markup.row(*buttons)


    return markup

def make_message(num_quest):
    global _data
    titles =  _data["titles"]
    text = make_text(num_quest)

    return f"🌿{num_quest}/21 *{titles[num_quest - 1]}*\n{text}"

def make_text(num_quest):
    global _data
    text = []
    access_list = _data["questions"][f"{num_quest}" ]

    for i in range(4):
        text.append(f'{i + 1}.{access_list[i]}')
    text = '\n'.join(text)
    return text



def send_results(chat_id):
    
    result_message = make_result_message(chat_id)
    bot.send_message(chat_id, f"{result_message}")

def make_result_message(chat_id):
    global mapping
    result = mapping[f"{chat_id}"]["result"]

    smiles = _all_data["results"]["smiles"]
    var_reply = _all_data["results"]["reply"]
    
    if  result <= 13:
        i = 0
    elif result in range(14, 20):
        i = 1
    elif result in range(21, 29):
        i = 2
    else:
        i = 3

    return f"Ваш реузльтат составляет {result} {smiles[i]}\n{var_reply[i]}."

if __name__ == "__main__":
    bot.polling(non_stop=True)

