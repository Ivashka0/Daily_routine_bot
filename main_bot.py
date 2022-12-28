import telebot
import os
import json
from telebot import types
import datetime

config = {
    "name": "TaskManager",
    "token": "5888172256:AAEVv_5NIBoO_q2YzOwyXCubtHOM21Zkyag"
}

fedo = telebot.TeleBot(config["token"])

add_username = ""


@fedo.callback_query_handler(func=lambda call: True)
def callback_data(call):
    a = call.data.split()
    if a[2] == "d":
        deleter(a[1], a[0])
    else:
        completer(a[1], a[0])


@fedo.message_handler(commands=["start"])
def authorization(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Регистрация")
    btn2 = types.KeyboardButton("Авторизация")
    markup.add(btn1, btn2)
    fedo.send_message(message.chat.id, 'Начальное меню', reply_markup=markup)


@fedo.message_handler(commands=["menu"])
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить задание")
    btn2 = types.KeyboardButton("Сортировать задания")
    btn3 = types.KeyboardButton("Вывести список заданий")
    btn4 = types.KeyboardButton("Другие функции")
    markup.add(btn1, btn2, btn3, btn4)
    fedo.send_message(message.chat.id, 'Главное меню', reply_markup=markup)


@fedo.message_handler(commands=["sorting_menu"])
def sort(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Сортировка от самой старой")
    btn2 = types.KeyboardButton("Поиск по определенной дате")
    btn3 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3)
    fedo.send_message(message.chat.id, 'Сортировочное меню', reply_markup=markup)


@fedo.message_handler(commands=["other_menu"])
def other(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить задание пользователю")
    btn2 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2)
    fedo.send_message(message.chat.id, 'Остальные функции', reply_markup=markup)


@fedo.message_handler(content_types=["text"])
def get_text(message):
    with open("userdata.json", "r") as json_file:
        dicti = json.load(json_file)
    if message.text == "Регистрация":
        password = fedo.send_message(message.chat.id,
                                     f"Напишите пароль:")
        fedo.register_next_step_handler(password, register)
    elif message.text == "Авторизация":
        password = fedo.send_message(message.chat.id,
                                     f"Напишите пароль для входа:")
        fedo.register_next_step_handler(password, login)
    elif message.text == "Вывести список заданий" and message.from_user.username in dicti:
        print_all_tasks(message)
    elif message.text == "Назад" and message.from_user.username in dicti:
        main_menu(message)
    elif message.text == "Добавить задание" and message.from_user.username in dicti:
        name = fedo.send_message(message.chat.id,
                                 f"Напишите название и дату в формате: Купить торт/12-12-2012")
        fedo.register_next_step_handler(name, add_task)
    elif message.text == "Сортировать задания" and message.from_user.username in dicti:
        sort(message)
    elif message.text == "Сортировка от самой старой" and message.from_user.username in dicti:
        sorting_by_date(message)
    elif message.text == "Поиск по определенной дате" and message.from_user.username in dicti:
        date = fedo.send_message(message.chat.id,
                                 f"Напишите дату в формате: 12-12-2012")
        fedo.register_next_step_handler(date, find_by_date)
    elif message.text == "Другие функции" and message.from_user.username in dicti:
        other(message)
    elif message.text == "Добавить задание пользователю" and message.from_user.username in dicti:
        date = fedo.send_message(message.chat.id,
                                 f"Напишите имя другого пользователя")
        fedo.register_next_step_handler(date, users_add_tasks)
    else:
        if message.from_user.username in dicti and message.from_user.username in dicti:
            fedo.send_message(message.chat.id, "Ничего не найдено")
        else:
            fedo.send_message(message.chat.id, "Зарегистрируйтесь,пожалуйста")


def register(message):
    with open("userdata.json", "r") as json_file:
        dicti = json.load(json_file)

    if message.from_user.username in dicti:
        fedo.send_message(message.chat.id, f"Имя - {message.from_user.username} уже зарегестрировано")
    else:
        dicti[message.from_user.username] = {"id": message.from_user.id, "password": message.text}
        with open("userdata.json", "w") as json_file:
            json.dump(dicti, json_file, indent=4, sort_keys=True)
        fedo.send_message(message.chat.id, f"Зарегестрировано")
        main_menu(message)


def login(message):
    with open("userdata.json", "r") as json_file:
        dicti = json.load(json_file)

    if message.from_user.username in dicti:
        if message.text == dicti[message.from_user.username]["password"]:
            fedo.send_message(message.chat.id, f"Вы вошли")
            main_menu(message)
        else:
            fedo.send_message(message.chat.id, f"Попытайтесь еще раз")
    else:
        fedo.send_message(message.chat.id, f"{message.from_user.username} еще не зарегистрирован")


def print_all_tasks(message):
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)
    if message.from_user.username in dicti1:
        for ele in range(len(dicti1[message.from_user.username])):
            if len(dicti1[message.from_user.username]) > 0 \
                    and dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[ele]][
                'completed']:
                inlines = telebot.types.InlineKeyboardMarkup()
                inlines.add(telebot.types.InlineKeyboardButton(text=f"Удалить задание",
                                                               callback_data=f"{list(dicti1[message.from_user.username].keys())[ele]} {message.from_user.username} d"))
                fedo.send_message(message.chat.id,
                                  f"✅{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[ele]]['headline']}✅\n "
                                  f"Дата создания: "
                                  f"{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[ele]]['date']}",
                                  reply_markup=inlines)
            elif len(dicti1[message.from_user.username]) > 0 \
                    and not dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[ele]][
                'completed']:
                inlines = telebot.types.InlineKeyboardMarkup()
                inlines.add(telebot.types.InlineKeyboardButton(text=f"Выполнить задание",
                                                               callback_data=f"{list(dicti1[message.from_user.username].keys())[ele]} {message.from_user.username} c"))
                inlines.add(telebot.types.InlineKeyboardButton(text=f"Удалить задание",
                                                               callback_data=f"{list(dicti1[message.from_user.username].keys())[ele]} {message.from_user.username} d"))
                fedo.send_message(message.chat.id,
                                  f"{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[ele]]['headline']}\n"
                                  f"Дата создания: "
                                  f"{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[ele]]['date']}",
                                  reply_markup=inlines)
            else:
                fedo.send_message(message.chat.id, f"Нету заданий ")
    else:
        fedo.send_message(message.chat.id, f"Добавьте 1 задание")


def completer(username, number):
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)
    dicti1[username][number]['completed'] = True
    with open("tasks.json", "w") as json_file:
        json.dump(dicti1, json_file, indent=4, sort_keys=True)


def deleter(username, number):
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)
    del dicti1[username][number]
    with open("tasks.json", "w") as json_file:
        json.dump(dicti1, json_file, indent=4, sort_keys=True)


def add_task(message):
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)
    data = message.text.split('/')
    try:
        date = datetime.datetime.strptime(data[1], "%d-%m-%Y")
        datetime.datetime.strftime(date, "%d-%m-%Y")
        access = True
    except ValueError as warning:
        print(warning)
        fedo.send_message(message.chat.id, str(warning))
        access = False
    if len(data) == 2 and access:
        if not message.from_user.username in dicti1:
            dicti1[message.from_user.username] = {}
            print(dicti1)
            dicti1[message.from_user.username]["1"] = {
                "completed": False,
                "date": f"{data[1]}",
                "headline": f"{data[0]}"}
            fedo.send_message(message.chat.id, f"Добавлено")
        elif len(dicti1[message.from_user.username]) > 0 and message.from_user.username in dicti1:
            dicti1[message.from_user.username][str(len(dicti1[message.from_user.username]) + 1)] = {
                "completed": False,
                "date": f"{data[1]}",
                "headline": f"{data[0]}"}
            fedo.send_message(message.chat.id, f"Добавлено")
        else:
            dicti1[message.from_user.username]["1"] = {
                "completed": False,
                "date": f"{data[1]}",
                "headline": f"{data[0]}"}
            fedo.send_message(message.chat.id, f"Добавлено")
    else:
        fedo.send_message(message.chat.id, f"Вводите в правильном формате!")
    print(dicti1)
    with open("tasks.json", "w") as json_file:
        json.dump(dicti1, json_file, indent=4, sort_keys=True)


def sorting_by_date(message):
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)

    dates = [datetime.datetime.strptime(
        dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[i]]['date'], "%d-%m-%Y") for
        i in
        range(len(dicti1[message.from_user.username]))]
    dates.sort()
    sorteddates = [datetime.datetime.strftime(ts, "%d-%m-%Y") for ts in dates]
    dict_data = {message.from_user.username: {}}
    for i in sorteddates:
        for element in range(len(dicti1[message.from_user.username])):
            if dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]][
                'date'] == i:
                dict_data[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]] = \
                    dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]]
                print(dict_data)
    for element in range(len(dict_data[message.from_user.username])):
        if dict_data[message.from_user.username][list(dict_data[message.from_user.username].keys())[element]][
            'completed']:
            inlines = telebot.types.InlineKeyboardMarkup()
            inlines.add(telebot.types.InlineKeyboardButton(text=f"Удалить задание",
                                                           callback_data=f"{list(dict_data[message.from_user.username].keys())[element]} "
                                                                         f"{message.from_user.username} d"))
            fedo.send_message(message.chat.id,
                              f"✅{dict_data[message.from_user.username][list(dict_data[message.from_user.username].keys())[element]]['headline']}✅\n "
                              f"Дата создания: "
                              f"{dict_data[message.from_user.username][list(dict_data[message.from_user.username].keys())[element]]['date']}",
                              reply_markup=inlines)
        elif not dict_data[message.from_user.username][list(dict_data[message.from_user.username].keys())[element]][
            'completed']:
            inlines = telebot.types.InlineKeyboardMarkup()
            inlines.add(telebot.types.InlineKeyboardButton(text=f"Выполнить задание",
                                                           callback_data=f"{list(dict_data[message.from_user.username].keys())[element]} "
                                                                         f"{message.from_user.username} c"))
            inlines.add(telebot.types.InlineKeyboardButton(text=f"Удалить задание",
                                                           callback_data=f"{list(dict_data[message.from_user.username].keys())[element]} "
                                                                         f"{message.from_user.username} d"))
            fedo.send_message(message.chat.id,
                              f"{dict_data[message.from_user.username][list(dict_data[message.from_user.username].keys())[element]]['headline']}\n"
                              f"Дата создания: "
                              f"{dict_data[message.from_user.username][list(dict_data[message.from_user.username].keys())[element]]['date']}",
                              reply_markup=inlines)


def find_by_date(message):
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)
    try:
        date = datetime.datetime.strptime(message.text, "%d-%m-%Y")
        datetime.datetime.strftime(date, "%d-%m-%Y")
        access = True
    except ValueError as warning:
        print(warning)
        fedo.send_message(message.chat.id, str(warning))
        access = False
    if access:
        for element in range(len(dicti1[message.from_user.username])):
            if dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]]['date'] \
                    == message.text:
                if len(dicti1[message.from_user.username]) > 0 \
                        and \
                        dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]][
                            'completed']:
                    inlines = telebot.types.InlineKeyboardMarkup()
                    inlines.add(telebot.types.InlineKeyboardButton(text=f"Удалить задание",
                                                                   callback_data=f"{list(dicti1[message.from_user.username].keys())[element]} {message.from_user.username} d"))
                    fedo.send_message(message.chat.id,
                                      f"✅{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]]['headline']}✅\n "
                                      f"Дата создания: "
                                      f"{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]]['date']}",
                                      reply_markup=inlines)
                elif len(dicti1[message.from_user.username]) > 0 \
                        and not \
                dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]][
                    'completed']:
                    inlines = telebot.types.InlineKeyboardMarkup()
                    inlines.add(telebot.types.InlineKeyboardButton(text=f"Выполнить задание",
                                                                   callback_data=f"{list(dicti1[message.from_user.username].keys())[element]} {message.from_user.username} c"))
                    inlines.add(telebot.types.InlineKeyboardButton(text=f"Удалить задание",
                                                                   callback_data=f"{list(dicti1[message.from_user.username].keys())[element]} {message.from_user.username} d"))
                    fedo.send_message(message.chat.id,
                                      f"{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]]['headline']}\n"
                                      f"Дата создания: "
                                      f"{dicti1[message.from_user.username][list(dicti1[message.from_user.username].keys())[element]]['date']}",
                                      reply_markup=inlines)
                else:
                    fedo.send_message(message.chat.id, f"Нету заданий ")
            else:
                continue
    else:
        fedo.send_message(message.chat.id, f"Вводите в правильном формате!")


def users_add_tasks(message):
    global add_username
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)
    add_username = message.text
    date = fedo.send_message(message.chat.id,
                             f"Напишите название и дату в формате: Купить торт/12-12-2012")

    if add_username in dicti1:
        fedo.register_next_step_handler(date, add_other)
    else:
        fedo.send_message(message.chat.id, f"Пользователь или не зарегестрирован,или не добавил первое задание")


def add_other(message):
    print(add_username)
    data = message.text.split("/")[1]
    date1 = message.text.split("/")
    print(data)
    with open("tasks.json", "r", encoding="utf8") as json_file:
        dicti1 = json.load(json_file)
    try:
        date = datetime.datetime.strptime(data, "%d-%m-%Y")
        datetime.datetime.strftime(date, "%d-%m-%Y")
        access = True
    except ValueError as warning:
        print(warning)
        fedo.send_message(message.chat.id, str(warning))
        access = False
    if access:
        dicti1[add_username][str(int(list(dicti1[add_username].keys())[-1]) + 1)] = {
            "completed": False,
            "date": f"{date1[1]}",
            "headline": f"{date1[0]}"}
        fedo.send_message(message.chat.id, f"Добавлено")
        with open("tasks.json", "w") as json_file:
            json.dump(dicti1, json_file, indent=4, sort_keys=True)
    else:
        fedo.send_message(message.chat.id, f"Вводите в правильном формате!")


fedo.polling(none_stop=True, interval=0)
