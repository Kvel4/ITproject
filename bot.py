import telebot
import json
import shelve
import config
import requests


class db():
    def write_user(dict, user_id):
        with open('json_data', 'r', encoding='utf-8') as inp:
            list_of_dict = json.load(inp)
            list_of_dict[str(user_id)] = dict

            with open('json_data', 'w', encoding='utf-8') as data:
                json.dump(list_of_dict, data, indent=4, ensure_ascii=False)

    def get_user(self):
        with open('json_data', 'r', encoding='utf-8') as inp:
            return json.load(inp)

    def get_priority(self):
        with open('json_priority', 'r', encoding='utf-8') as inp:
            return json.load(inp)

    def write_priority(dict, user_id):
        with open('json_priority', 'r', encoding='utf-8') as inp:
            list_of_dict = json.load(inp)
            list_of_dict[str(user_id)] = dict

            with open('json_priority', 'w', encoding='utf-8') as data:
                json.dump(list_of_dict, data, indent=4, ensure_ascii=False)


class user(dict):
    def __init__(self, message_id):
        self.quest = db.get_user(1)
        self.quest[str(message_id)] = {
            'name': '',
            'event_type': [],
            'city_name': '',
            'age_restriction': '',
            'hobby': []
            }


class states():
    start = '0'
    name = '1'
    event = '2'
    city = '3'
    age = '4'
    hobby = '5'
    usage = '6'

    def get_current_state(user_id):
        with shelve.open(config.db_file) as db:
            try:
                return db[str(user_id)]
            except KeyError:  # Если такого ключа почему-то не оказалось
                pass  # значение по умолчанию - начало диалога

    # Сохраняем текущее «состояние» пользователя в нашу базу
    def set_state(user_id, value):
        with shelve.open(config.db_file) as db:
            try:
                db[str(user_id)] = value
                return True
            except:
                return -1


class priority(dict):
    def __init__(self, message_id, params):
        self.dictionary = db.get_priority(1)
        self.dictionary[str(message_id)] = {
            'request': requests.get('https://kudago.com/public-api/v1.4/events/', params=params).json()['results'],
            'amount': 20,
            'priority': [0 for i in range(100)],
            'index': [],
            'set': [],
            'temp': 0,
            'counter': 0,
        }
        db.write_priority(self.dictionary[str(message_id)], message_id)


bot = telebot.TeleBot('534489748:AAHshR88itmKmN_5HSQZeMdZ1CY3zTz60aI')


@bot.message_handler(commands=['start'])
def questionary(message):
    bot.send_message(message.chat.id, 'Приветствую вас, о величайший лорд тьмы. '
                                      'Для того чтобы выполнить свою роль, мне необходимо узнать о ваших предпочтениях.'
                                      ' Надеюсь ваше высочесто соизволит ответить на несколько вопросов')

    events_names = ['festival',
                    'cinema',
                    'exhibition',
                    'concert',
                    'meeting',
                    'theater',
                    'yarmarki-razvlecheniya-yarmarki',
                    'party',
                    'masquerade'
                    ]
    cities = ['Москва', 'Санкт-Петербург']
    age_restriction = ['18+', 'Нет']
    hobbies = ['музыка',
               'живопись',
               'архитектруа и дизайн',
               'современное искусство',
               'новые технологии',
               'наука',
               'кулинария'
               ]

    bot.send_message(message.chat.id, "Как я могу к вам обращаться?")
    states.set_state(message.chat.id, states.name)
    person = user(message.chat.id)

    @bot.message_handler(func= lambda message: states.get_current_state(message.chat.id) == states.name)
    def i_know_de_name(message):
        person.quest[str(message.chat.id)]['name'] = message.text
        states.set_state(message.chat.id, states.event)

        markup = telebot.types.ReplyKeyboardMarkup()
        for event in events_names:
            markup.add(event)
        markup.add('Перейти к следующему вопросу')
        bot.send_message(message.chat.id,
                         ' Для начала давайте выясним какой тип ивентов вы предпочитаете(можно указать несколько)',
                         reply_markup=markup)

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.event and message.text in events_names)
    def event_type(message):
        if message.text not in person.quest[str(message.chat.id)]['event_type']:
            person.quest[str(message.chat.id)]['event_type'].append(message.text)

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.event and message.text == 'Перейти к следующему вопросу')
    def go_to_next(message):
        states.set_state(message.chat.id, states.city)

        markup = telebot.types.ReplyKeyboardMarkup()
        for city in cities:
            markup.add(city)
        markup.add('Перейти к следующему вопросу')

        bot.send_message(message.chat.id, 'Теперь выберите город', reply_markup=markup)

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.city and message.text in cities)
    def city_name(message):
        person.quest[str(message.chat.id)]['city_name'] = message.text

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.city and message.text == 'Перейти к следующему вопросу')
    def go_to_next1(message):
        states.set_state(message.chat.id, states.age)

        markup = telebot.types.ReplyKeyboardMarkup()
        for restriction in age_restriction:
            markup.add(restriction)
        markup.add('Перейти к следующему вопросу')

        bot.send_message(message.chat.id,
                         'У вас есть пожелания по возрастному ограничению?',
                         reply_markup=markup)

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.age and message.text in age_restriction)
    def restriction(message):
        person.quest[str(message.chat.id)]['age_restriction'] = message.text

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.age and message.text == 'Перейти к следующему вопросу')
    def go_to_next2(message):
        states.set_state(message.chat.id, states.hobby)

        markup = telebot.types.ReplyKeyboardMarkup()
        for hobby in hobbies:
            markup.add(hobby)
        markup.add('Закончить опрос')

        bot.send_message(message.chat.id, 'Укажите ваши увлечения', reply_markup=markup)

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.hobby and message.text in hobbies)
    def hobby(message):
        if message.text not in person.quest[str(message.chat.id)]['hobby']:
            person.quest[str(message.chat.id)]['hobby'].append(message.text)

    @bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == states.hobby and message.text == 'Закончить опрос')
    def end(message):
        db.write_user(person.quest[str(message.chat.id)], message.chat.id)
        states.set_state(message.chat.id, states.usage)
        
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Спасибо, анкета составлена.'
                         ' Если вы заходите что-то изменить в ней еще раз активируйте команду /start',
                         reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Список доступных команд:\n'
                                      '/start - Заполнение или перезаполнение анкеты\n'
                                      '/subway - \n'
                                      '/geo - \n'
                                      '/general -')


@bot.message_handler(commands=['geo'])
def geolocation(message):
    # Эти параметры для клавиатуры необязательны, просто для удобства
    keyboard = telebot.types.ReplyKeyboardMarkup()
    button_geo = telebot.types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id,
                     "Отправь мне свое местоположение, жалкий человечишка!",
                     reply_markup=keyboard)


@bot.message_handler(commands=['subway'])
def subway(message):
    bot.send_message(message.chat.id, 'Введи станцию метро, рядом с которой хочешь увидеть события')


@bot.message_handler(commands=['general'])
def general(message):
    params = {
        'page_size': '100',
        'fields': 'id,dates,title,short_title,slug,place,description,body_text,location,categories,tagline,'
                  'age_restriction,price,is_free,site_url,tags,participants',
        'expand': 'place,location'
    }

    p = priority(message.chat.id, params)
    u = db.get_user(1)

    p.dictionary[str(message.chat.id)]['counter'] = 0
    for event in p.dictionary[str(message.chat.id)]['request']:
        for key in ['event_type', 'hobby']:
            for element in u[str(message.chat.id)][key]:
                if element in event['categories']:
                    p.dictionary[str(message.chat.id)]['priority'][p.dictionary[str(message.chat.id)]['counter']] += 1
        p.dictionary[str(message.chat.id)]['counter'] += 1

    p.dictionary[str(message.chat.id)]['set'] = set(p.dictionary[str(message.chat.id)]['priority'])

    while len(p.dictionary[str(message.chat.id)]['index']) != p.dictionary[str(message.chat.id)]['amount'] and len(p.dictionary[str(message.chat.id)]['set']) > 0:
        p.dictionary[str(message.chat.id)]['temp'] = max(p.dictionary[str(message.chat.id)]['set'])
        p.dictionary[str(message.chat.id)]['set'].remove(p.dictionary[str(message.chat.id)]['temp'])
        for i in range(len(p.dictionary[str(message.chat.id)]['priority'])):
            if p.dictionary[str(message.chat.id)]['priority'][i] == p.dictionary[str(message.chat.id)]['temp']:
                p.dictionary[str(message.chat.id)]['index'].append(i)

    for i in p.dictionary[str(message.chat.id)]['index']:
        print(p.dictionary[str(message.chat.id)]['request'][i])

if __name__ == '__main__':
    bot.polling(none_stop=True)
