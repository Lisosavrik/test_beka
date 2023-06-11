import telebot
import json
from telebot import types 
import time 
import random
from file_utils import get_file_json



bot = telebot.TeleBot('6170027400:AAHqHQ08cQiSD4fD4MkVzlqXMc-VIPXBIoQ')
_data = get_file_json("data.json")
mapping = {}


def init_user(message):
    chat_id = message.chat.id
    start_id = message.id

    user = {
        "key": 1,
        "result": 0,
        "start_id": start_id
    }

    if f"{chat_id}" in mapping:
        user["start_id"] = mapping[f"{chat_id}"]["start_id"]
    
    mapping[f"{chat_id}"] = user
    

@bot.message_handler(commands= ['start'])
def start(message):
    init_user(message)

    chat_id = message.chat.id 
    # if f"{chat_id}" not in mapping["start_id"]:
    #     mapping['start_id'].update({f"{chat_id}": start_id})



    text1 = """
    Привет! 👀\nВы можете пойти к терапевту, а можете ставить себе диагнозы сами с помощью телеграмм-ботов, созданных непрофессионалами!
    """

    markup = types.InlineKeyboardMarkup()
    mar1 = types.InlineKeyboardButton("Ставить себе диагноз 🥸", callback_data="explanation")
    mar2 = types.InlineKeyboardButton("Обратиться к психотерапевту 🌚", callback_data="fack_you")
    markup.row(mar1, mar2)
    bot.send_message(chat_id,  f'{text1}', reply_markup=markup)

@bot.callback_query_handler(func= lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    global mapping
    key = mapping[f"{chat_id}"]["key"]
    start_id = mapping[f"{chat_id}"]["start_id"]


    if call.data == "explanation":
        text2 = \
"""*Внимательно прочтите группы утверждений, которые будут ниже🧐*
В каждой из них отметьте тот пункт, который наиболее полно отражает ваше состояние в последние *две недели*, включая сегодняшний день.
Если в какой-то из групп вам сложно определиться между двумя-тремя вариантами, выбирайте более печальный!
Вы готовы?"""

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ПРОДОЛЖИТЬ", callback_data="start_test"))

        bot.send_photo(chat_id,  photo=open('have_a_drink.jpeg', 'rb'))
        time.sleep(1)
        bot.send_message(chat_id,  f'{text2}', reply_markup=markup, parse_mode="Markdown")

    elif call.data == "fack_you":
        chat_id = call.message.chat.id
        message_id = call.message.id 

        i = 0
        while message_id - i != start_id:
            bot.delete_message(chat_id, message_id - i)
            i += 1

        bot.delete_message(chat_id, start_id)
        
        del mapping[f"{chat_id}"]["start_id"]


        bot.send_message(chat_id, "Ну и иди нахуй!")

    
        
    elif call.data == "start_test":
        bot.send_message(chat_id, "Приступаем!")
        get_questions(call.message, 1)
        
    else:
        calldata = json.loads(call.data)
        num_quest = int(calldata["num_quest"])
        command = int(calldata["command"])

        if num_quest == key and  num_quest < 21:

            var_answers = [
                ["Отлично! 💅", "Йоу-йоу, круто!", "Неплохо! 🤔", "У тебя не все потеряно!"],
                ["Оу 😦", "Не повезло тебе!", "Слегка прескорбно 🤧", "У тебя сложная ситуация"],
                ["Удивляешь!", "Печально 😓", "Ты конечно даешь 😱", "Жуть 🫢" ],
                ["О ужас! 😖", "Врагу не пожелаешь! 😟", "Твоя жизнь - к деньгам психологу 💸", "Жаль этого добряка 😬"],
                ["С этим явный дисбаланс 😳", "Тут знать бы норму!😬", "Перебор! 🫣", "Не маловато? 😬"]
            ]


            which_list = command if key not in [15, 20] else 4



        

            bot.send_message(chat_id, var_answers[which_list][random.randint(0, 3)])
            get_questions(call.message, (num_quest + 1))

            mapping[f"{chat_id}"]["result"] += command
            mapping[f"{chat_id}"]["key"] += 1
        else: 
            mapping[f"{chat_id}"]["result"] += command
            results(chat_id)


def get_questions(message, num_quest):
    global _data
    titles =  _data["titles"]
    chat_id = message.chat.id
    markup = make_markup(num_quest)
    text = make_text(num_quest)

    time.sleep(1)
    bot.send_message(chat_id, f"🌿{num_quest}/21 *{titles[num_quest - 1]}*\n{text}", reply_markup=markup, parse_mode="Markdown")

def make_markup(num_questions):
    markup = types.InlineKeyboardMarkup()
    buttons = []

    for i in range(1, 5)  :
        make_btn = types.InlineKeyboardButton
        smiles = ['😃', '😳', '😞', '😫']

        calldata_json = json.dumps({"num_quest": f'{num_questions}', "command": f'{i - 1}' })
        buttons.append(make_btn(f'{i}{smiles[i - 1]}', callback_data = calldata_json))
    markup.row(*buttons)


    return markup

def make_text(num_quest):
    global _data
    text = []
    access_list = _data["questions"][f"{num_quest}" ]

    for i in range(4):
        text.append(f'{i + 1}.{access_list[i]}')
    text = '\n'.join(text)
    return text

def results(chat_id):
    global mapping
    result = mapping[f"{chat_id}"]["result"]
    

    if  result <= 13:
        i = 0
    elif result in range(14, 20):
        i = 1
    elif result in (21, 29):
        i = 2
    else:
        i = 3

    smiles = ['😋', '😒', '😖', '😭']
    var_answers = [
            "У вас нет депрессии, не тратьте время на ипохондрию! (0–13)",
            "Вероятна лёгкая депрессия (субдепрессия) 14–19 ",
            "Вероятна умеренная депрессия! Пора пить таблетки (20–28)",
            "Зовите на помощь, у вас тяжёлая депрессия. Состояние тем сложнее, чем больше количество баллов (29–63)"

    ]
    bot.send_message(chat_id, f"Ваш реузльтат составляет {result} {smiles[i]}\n{var_answers[i]}.")





if __name__ == "__main__":
    bot.polling(non_stop=True)

