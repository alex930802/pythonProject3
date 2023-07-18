import vk_api
from sqlalchemy import create_engine
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from bot import Vkinder
from config import access_token, token_group, db_url_object
from database import Base, add_profile, check_profile


class Vkinderinterface():
    def __init__(self, token_group, access_token):
        self.vk = vk_api.VkApi(token=token_group)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_bot = Vkinder(access_token)
        self.params = {}
        self.tools = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )

    def data_age(self, user_id):
        self.message_send(user_id, 'Введите возраст: ')
        message, user_id = self.event_handler()
        age_prof = str(message)
        age_user = self.vk_bot.params['age']
        for age_info in age_user:
            if age_info['age'] == age_prof.title():
                self.message_send(user_id, f'Поиск по возрасту {age_prof.title()} лет')
                return age_prof.title()

    def data_sex(self, user_id):
        self.message_send(user_id, 'Введите пол: ')
        message, user_id = self.event_handler()
        sex_prof = str(message)
        sex_user = self.vk_bot.params['sex']
        for sex_info in sex_user:
            if sex_info['sex'] == sex_prof.title():
                self.message_send(user_id, f'Поиск противоположного пола {sex_prof.title()}')
                return sex_prof.title()

    def data_city(self, user_id):
        self.message_send(user_id, 'Введите пол: ')
        message, user_id = self.event_handler()
        city_prof = str(message)
        city_user = self.vk_bot.params['city']
        for city_info in city_user:
            if city_info['title'] == city_prof.title():
                self.message_send(user_id, f'Поиск по введному названия города {sex_prof.title()}')
                return city_prof.title()

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.params = self.vk_bot.get_users(event.user_id)
                    if self.params['city'] is None:
                        self.message_send(
                            event.user_id, f'Привет, {self.params["name"]}!\n'
                                           f'Для продолжения  укажи свой город')
                        event.to_me = self.data_city(event.user_id)
                    elif self.params['age'] is None:
                        self.message_send(
                        event.user_id, f'Привет, {self.params["name"]}!\n'
                        f'Укажите свой возраст')
                        event.to_me = self.data_age(event.user_id)
                    elif self.params['sex'] is None:
                        self.message_send(
                        event.user_id, f'Привет, {self.params["name"]}!\n'
                        f'Укажите свой пол')
                        event.to_me = self.data_sex(event.user_id)
                    else:
                        self.message_send(event.user_id, f'Привет {self.params["name"]}')
                elif event.text.lower() == 'поиск':
                    self.message_send(
                        event.user_id, 'Начинаем поиск')

                    if self.tools:
                        tool = self.tools.pop()
                        photos = self.vk_bot.get_photo(tool['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.tools = self.vk_bot.users_search(
                            self.params, self.offset)
                        tool = self.tools.pop()

                        engine = create_engine(db_url_object)
                        num_users = 0
                        all_users = set()

                        while tool and num_users < 1:
                            if str(tool['id']) not in all_users:
                                all_users.add(str(tool['id']))
                                num_users += 1

                                if check_profile(engine, tool):
                                    self.message_send(event.user_id, f"{tool['name']} уже есть в базе данных.")
                                    continue
                        photos = self.vk_bot.get_photo(tool["id"])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 50

                        self.message_send(
                            event.user_id,
                            f'имя: {tool["name"]} ссылка: vk.com/{tool["id"]}',
                            attachment=photo_string
                        )
                        add_profile(engine, event.user_id, tool['id'])

                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч')

                else:
                    self.message_send(
                        event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot_interface = Vkinderinterface(token_group, access_token)
    bot_interface.event_handler()

    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
