import vk_api
import random
import time
import sqlite3
import json
import config


conn = sqlite3.connect("cinemas.db")
cursor = conn.cursor()

newline = '\n'

test = list(cursor.execute("SELECT * FROM sessions WHERE hall_id = '11' AND date = '2019-12-12' AND name = 'Джуманджи: Новый уровень, 12+'"))

token = config.TOKEN

test_data = list(cursor.execute("SELECT name FROM cinema_halls"))


# Нумерация кинотеатров
count_list = []
for iteration in range(len(test_data)):
    count_list.append(str(iteration+1))


# Информация о датах определенного кинотеатра
count_dates_list = []
for iteration in range(len(test_data)):
    count_dates_list.append("кинотеатр №" + str(iteration+1) + ", посмотреть даты")


# Информация о сеансах в определенный день
sessions_in_date_list = []
for iteration in range(len(test_data)):
    all_dates = list(cursor.execute(f"SELECT DISTINCT date FROM sessions WHERE hall_id = '{iteration+1}' LIMIT 12"))
    for jteration in range(len(all_dates)):
        sessions_in_date_list.append(str(iteration+1) + " | " + str(all_dates[jteration][0]))


vk = vk_api.VkApi(token=token)

vk._auth_token()


# Выбранный кинотеатр
picked_cinema_hall = ''


################ ЗАПУСК БОТА ##################

while True:
    try:
        messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unanswered"})
        if messages["count"] >= 1:
            id = messages["items"][0]["last_message"]["from_id"]
            body = messages["items"][0]["last_message"]["text"]


            # КОМАНДА "ВЫБРАТЬ КИНОТЕАТР"


            if body.lower() == "выбрать кинотеатр":

                                        ### JSON ###
                lenght = len(list(cursor.execute("SELECT name FROM cinema_halls")))

                buttons_in_line_dict = []

                s = 0
                d = 0
                main_cinemas_lst = [[], [], [], []]
                for count in range(lenght):
                    if (count % 4 == 0):
                        s = d
                        num_of_list_cinemas = count // 4
                    count = count % 4
                    main_cinemas_lst[num_of_list_cinemas].append(
                        {"action": {"type": "text", "label": str(count + s + 1)}, "color": "default"})
                    # print(count + s)
                    d += 1

                keyboard_hi_dict = {
                    "one_time": True,
                    "buttons": main_cinemas_lst
                }

                with open('find_cinema_keyboard.json', 'w') as f:
                    json.dump(keyboard_hi_dict, f)
                                        ###########

                cinemas = []
                for i in range(len(test_data)):
                    cinema_str_with_number = f"{i + 1}) {test_data[i][0].lstrip()}"
                    cinemas.append(cinema_str_with_number)

                lenght = len(cinemas)
                vk.method("messages.send", {"peer_id": id, "message": f'''Пожалуйста!
Вот список кинотеатров КАРО:

{newline.join(cinemas)}

Выбери номер кинотеатра, чтобы узнать информацию.''', "random_id": random.randint(1, 2147483647), "keyboard": open("find_cinema_keyboard.json", "r", encoding="UTF-8").read()})


            # КОМАНДА "НАЧАТЬ"


            elif body.lower() == "начать" or body.lower() == "привет":
                vk.method("messages.send", {"peer_id": id, "message": "Привет! Если хочешь выбрать кинотеатр из списка, нажми на кнопку \"Выбрать кинотеатр\"", "random_id": random.randint(1, 2147483647), "keyboard": open("keyboard_hi.json", "r", encoding="UTF-8").read()})


            # ИНФО О КИНОТЕАТРЕ


            elif str(body.lower()) in count_list:

                picked_cinema_hall = str(body.lower())

                                            ### JSON ###
                lenght = len(list(cursor.execute("SELECT name FROM cinema_halls")))

                main_cinemas_lst = [[], []]
                main_cinemas_lst[0].append(
                    {"action": {"type": "text", "label": "Кинотеатр №" + picked_cinema_hall + ", посмотреть даты"}, "color": "positive"})
                main_cinemas_lst[1].append(
                    {"action": {"type": "text", "label": "Выбрать кинотеатр"}, "color": "negative"})

                keyboard_hi_dict = {
                    "one_time": True,
                    "buttons": main_cinemas_lst
                }

                with open('find_date_of_cinema_keyboard.json', 'w') as f:
                    json.dump(keyboard_hi_dict, f)
                                             ###########


                picked_cinema_name = list(cursor.execute(f"SELECT name FROM cinema_halls WHERE id = '{int(body.lower())}'"))
                cinema_information_adress = list(cursor.execute(f"SELECT adress FROM cinema_halls WHERE id = '{int(body.lower())}'"))
                cinema_information_metro = list(cursor.execute(f"SELECT metro FROM cinema_halls WHERE id = '{int(body.lower())}'"))
                cinema_information_phone = list(cursor.execute(f"SELECT phone FROM cinema_halls WHERE id = '{int(body.lower())}'"))
                vk.method("messages.send", {"peer_id": id, "message": f'''Вот информация о кинотеатре под номером {str(body.lower())} \"{picked_cinema_name[0][0].lstrip()}\":

Адрес: {cinema_information_adress[0][0].lstrip()}
Метро: {cinema_information_metro[0][0].lstrip()}
Телефон: {cinema_information_phone[0][0].lstrip()}

Чтобы посмотреть доступные даты сеансов, нажмите на зеленую кнопку.''', "random_id": random.randint(1, 2147483647), "keyboard": open("find_date_of_cinema_keyboard.json", "r", encoding="UTF-8").read()})


            # ВЫВЕСТИ ДОСТУПНЫЕ ДАТЫ СЕАНСОВ


            elif str(body.lower()) in count_dates_list:

                                            #### JSON ####

                dates_one_day = list(cursor.execute("SELECT DISTINCT date FROM sessions LIMIT 8"))

                s = 0
                d = 0
                main_cinemas_lst = [[], [], [], [], []]

                for count in range(len(dates_one_day)):
                    if (count % 2 == 0):
                        s = d
                        num_of_list_cinemas = count // 2
                    count = count % 2
                    main_cinemas_lst[num_of_list_cinemas].append(
                        {"action": {"type": "text", "label": str(picked_cinema_hall) + " | " + dates_one_day[count + s][0]},
                         "color": "default"})
                    d += 1

                main_cinemas_lst[4].append({"action": {"type": "text", "label": "Выбрать кинотеатр"},
                         "color": "negative"})

                keyboard_hi_dict = {
                    "one_time": True,
                    "buttons": main_cinemas_lst
                }

                with open('find_session_by_date_keyboard.json', 'w') as f:
                    json.dump(keyboard_hi_dict, f)

                                            ##############

                dates_of_this_cinema = list(cursor.execute(f"SELECT DISTINCT date FROM sessions LIMIT 8"))
                operation_1 = str(body.lower())[11:]
                hall_id_pre = operation_1.split(',')
                hall_id = hall_id_pre[0]
                date_lst = []
                for i in range(len(dates_of_this_cinema)):
                    date_every = f"{dates_of_this_cinema[i][0]}"
                    date_lst.append(date_every)
                hall_name = list(cursor.execute(f"SELECT name FROM cinema_halls WHERE id = '{hall_id}'"))
                vk.method("messages.send", {"peer_id": id, "message": f'''Ближайшие даты сеансов в кинотеатре {hall_name[0][0].lstrip()}: 

{newline.join(date_lst)}

Нажмите на одну из предложенных кнопок, чтобы выбрать нужну дату.''', "random_id": random.randint(1, 2147483647), "keyboard": open("find_session_by_date_keyboard.json", "r", encoding="UTF-8").read()})


            elif body.lower() == 'команды':
                vk.method("messages.send",
                          {"peer_id": id, "message": f'''Доступные команды:

Привет
Хочу выбрать кинотеатр
''', "random_id": random.randint(1, 2147483647)})


            # ВЫВОД СЕАНСОВ НА ОПРЕДЕЛЕННУЮ ДАТУ


            elif str(body.lower()) in str(sessions_in_date_list):


                hall_id_and_date = str(body.lower()).split(' | ')
                name_of_session = list(cursor.execute(f"SELECT DISTINCT name FROM sessions WHERE hall_id = '{hall_id_and_date[0]}' AND date = '{hall_id_and_date[1]}'"))
                name_s = [i[0] for i in name_of_session]

                format_of_session = []
                for i in range(len(name_s)):
                    format_of_session.append(list(cursor.execute(f"SELECT DISTINCT session_format FROM sessions WHERE hall_id = '{hall_id_and_date[0]}' AND date = '{hall_id_and_date[1]}' AND name = '{name_s[i]}'")))
                formats_lst = []
                for i in format_of_session:
                    formats_of_one_film_lst = []
                    for j in i:
                        formats_of_one_film_lst.append(j[0])
                    formats_lst.append(formats_of_one_film_lst)

                time_of_session = []
                for n, i in enumerate(formats_lst):
                    time_of_session_with_format = []
                    for j in i:
                        time_of_session_with_format.append(list(cursor.execute(f"SELECT time FROM sessions WHERE hall_id = '{hall_id_and_date[0]}' AND date = '{hall_id_and_date[1]}' AND name = '{name_s[n]}' AND session_format = '{j}'")))
                    time_of_session.append(time_of_session_with_format)

                time_of_session_lst_every_film = []
                for every_film in time_of_session:
                    time_of_session_lst_every_format = []
                    for every_format in every_film:
                        time_of_session_lst_every_time = []
                        for every_session_time in every_format:
                            # print(every_session_time)
                            # print(every_session_time[0])
                            time_of_session_lst_every_time.append(every_session_time[0])
                        time_of_session_lst_every_format.append(time_of_session_lst_every_time)
                    time_of_session_lst_every_film.append(time_of_session_lst_every_format)

                main_session_str_block = ''
                for every_block_film in range(len(name_s)):
                    # print(name_s[every_block_film])
                    main_session_str_block += str(name_s[every_block_film]) + '\n'
                    for every_block_format in range(len(formats_lst[every_block_film])):
                        # print(formats_lst[every_block_film][every_block_format])
                        main_session_str_block += '|' + formats_lst[every_block_film][every_block_format] + '|\n'
                        for every_block_time in range(len(time_of_session_lst_every_film[every_block_film][every_block_format])):
                            # print(time_of_session_lst_every_film[every_block_film][every_block_format][every_block_time])
                            main_session_str_block += time_of_session_lst_every_film[every_block_film][every_block_format][every_block_time] + '\n'
                    main_session_str_block += '\n'

                current_cinema = list(cursor.execute(f"SELECT name FROM cinema_halls WHERE id = '{hall_id_and_date[0]}'"))
                vk.method("messages.send", {"peer_id": id, "message": f'''Сеансы на дату {hall_id_and_date[1]} в кинотеатре {current_cinema[0][0].lstrip()}:\n\n{main_session_str_block}''', "random_id": random.randint(1, 2147483647), "keyboard": open("keyboard_hi.json", "r", encoding="UTF-8").read()})


            # ПАСХАЛКИ

            ###

            # В ЛЮБОМ ДРУГОМ СЛУЧАЕ


            else:
                vk.method("messages.send", {"peer_id": id, "message": "Я не понимаю, что означает \"" + str(body.lower()) + "\". Попробуй нажать на кнопку \"Выбрать кинотеатр\"!", "random_id": random.randint(1, 2147483647), "keyboard": open("keyboard_hi.json", "r", encoding="UTF-8").read()})
    except Exception as E:
        time.sleep(1)
        # print("ошибка")

