import re
import sqlite3
import requests
from bs4 import BeautifulSoup


conn = sqlite3.connect("cinemas.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE sessions")
cursor.execute("DROP TABLE cinema_halls")

# таблица брендов
cursor.execute("""CREATE TABLE IF NOT EXISTS brand(
                id integer PRIMARY KEY,
                name text NOT NULL
                )""")
# таблица с кинотеатрами
cursor.execute("""CREATE TABLE IF NOT EXISTS cinema_halls(
                id integer PRIMARY KEY,
                brand_id integer NOT NULL,
                name text NOT NULL,
                adress text,
                metro text,
                phone text,
                FOREIGN KEY (brand_id) REFERENCES brand(id)
                )""")
# таблица с фильмами
cursor.execute("""CREATE TABLE IF NOT EXISTS cinemas(
                id integer PRIMARY KEY,
                name text NOT NULL,
                duration float NOT NULL,
                genres text NOT NULL
                )""")
# таблица с сеансами
cursor.execute("""CREATE TABLE IF NOT EXISTS sessions(
                id integer PRIMARY KEY,
                hall_id integer NOT NULL,
                name text text NOT NULL,
                date date NOT NULL,
                session_format text NOT NULL,
                time time NOT NULL
                )""")
#FOREIGN KEY (hall_id) REFERENCES cinema_halls(id)
#FOREIGN KEY (cinema_id) REFERENCES cinemas(id)
#cinema_id integer NOT NULL,

# Посмотреть список таблиц
lst_tables = list(cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"'))
print(lst_tables)


# Заносим бренд КАРО9
def add_brand(name):
    cursor.execute(f"INSERT INTO 'brand' ('id', 'name') VALUES (1, '{name}')")


# Заносим бренд КАРО в таблицу брендов
brand1 = 'КАРО'
# add_brand(brand1)

url = "https://karofilm.ru"
url_theaters = url + "/theatres"


#Регулярные выражения
def clearing(string):
    pattern = re.compile(r'[А-Яа-яЁё0-9]+')
    return pattern.findall(string)[0].strip()


#Находим информацию о кинотеатрах
def find_all_theaters_KARO(theaters):
    dct = {}
    metro_class = 'cinemalist__cinema-item__metro__station-list__station-item'
    for theater in theaters:
        dct[theater.findAll('h4')[0].text] = {
            'adress': theater.findAll('p')[0].text.split('+')[0].strip(),
            'metro': [clearing(i.text) for i in theater.findAll('li', class_=metro_class)],
            'phone': '+' + theater.findAll('p')[0].text.split('+')[-1],
            'data-id': theater['data-id']
        }
    return dct


# Даты, сеансы, время
def films(karo_theaters):
    films_class = 'cinema-page-item__schedule__row'
    table_class = 'cinema-page-item__schedule__row__board-row'
    left_class = table_class + '__left'
    rignt_class = table_class + '__right'
    date_class = 'widget-select'
    for theater in karo_theaters:
        dates = {}
        url_theater_id = url_theaters + '?id=' + karo_theaters[theater]['data-id']
        r = requests.get(url_theater_id)
        if r.status_code == 200:
            date_parser = BeautifulSoup(r.text, 'html.parser')
            date_list = date_parser.findAll('select', class_=date_class)[0]
            date_list = [i['data-id'] for i in date_list.findAll('option')]
            for date in date_list:

                url_theater_id_date = url_theater_id + '&date=' + date
                r = requests.get(url_theater_id_date)
                session = {}
                if r.status_code == 200:
                    films_parser = BeautifulSoup(r.text, 'html.parser')
                    films_list = films_parser.findAll('div', class_=films_class)
                    for film in films_list:
                        name = film.findAll('h3')
                        if name:
                            name = name[0].text
                            session_time = {}
                            for i in film.findAll('div', class_=table_class):
                                time_D = i.findAll('div', class_=left_class)[0].text.strip()
                                time = i.findAll('div', class_=rignt_class)[0].findAll('a')
                                time = [j.text for j in time]
                                session_time[time_D] = time
                            session[name] = session_time

                else:
                    print('Ненаход даты')
                dates[date] = session
        else:
            print('Ненаход кинотеатра')
        karo_theaters[theater]['dates'] = dates


# Поиск страницы с информацией о кинотеатрах
r = requests.get(url_theaters)
if r.status_code == 200:
    print("Страница найдена")
    print('Загрузка данных...')
    soup = BeautifulSoup(r.text, "html.parser")
    theaters = soup.findAll('li', class_='cinemalist__cinema-item')
    karo_theaters = find_all_theaters_KARO(theaters)
    films(karo_theaters)
else:
    print("Страница не найдена")

print(karo_theaters)


for i, v in enumerate(list(karo_theaters.items())):
    cursor.execute(f"INSERT INTO cinema_halls (id, brand_id, name) VALUES ({i+1}, 1,'{v[0]}')")
    adresses_dict = v[1]
    for j in list(adresses_dict.items()):
        if j[0] == 'adress':
            print("adress founded: " + j[1])
            cursor.execute(f"UPDATE cinema_halls SET adress = '{j[1]}' WHERE name = '{v[0]}'")
        if j[0] == 'metro':
            metro_str = ""
            for l in j[1]:
                print("metro founded: " + l)
                metro_str += l
                metro_str += " "
            cursor.execute(f"UPDATE cinema_halls SET metro = '{metro_str}' WHERE name = '{v[0]}'")
        if j[0] == 'phone':
            print("phone founded: " + j[1])
            cursor.execute(f"UPDATE cinema_halls SET phone = '{j[1]}' WHERE name = '{v[0]}'")
        if j[0] == 'dates':
            dates_dict = j[1]
            for film_in_dict in list(dates_dict.items()):
                # film_in_dict[0] - время сеанса
                every_film_dict = film_in_dict[1]
                for every_film in list(every_film_dict.items()):
                    # every_film[0] - название сеанса
                    every_film_clear = every_film[0].replace('\'', ' ')
                    format_2d_or_3d_dict = every_film[1]
                    for format_2d_or_3d in list(format_2d_or_3d_dict.items()):
                        # format_2d_or_3d[0] - 2D или 3D
                        session_time_dict = format_2d_or_3d[1]
                        print(format_2d_or_3d[0])
                        print(session_time_dict)
                        for every_session_time in session_time_dict:
                            # every_session_time - время сеанса список
                            cursor.execute(f"INSERT INTO sessions (hall_id, name, date, session_format, time) VALUES ('{i+1}', '{every_film_clear}', '{film_in_dict[0]}', '{format_2d_or_3d[0]}', '{every_session_time}')")



cursor.execute("SELECT * FROM cinema_halls").fetchall()
# Посмотреть таблицу cinema_halls
lst_cinemas = list(cursor.execute('SELECT * FROM cinema_halls'))
print(lst_cinemas)

lst_sessions = list(cursor.execute('SELECT * FROM sessions'))
print(lst_sessions)

conn.commit()
