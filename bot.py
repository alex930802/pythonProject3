from pprint import pprint
import vk_api
from config import access_token
from datetime import datetime
from vk_api.exceptions import ApiError
from operator import itemgetter


class Vkinder:
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)

    def age(self,bdate):
        user_year = bdate.split('.')[2] if bdate else None
        today_year = datetime.now().year
        return today_year - int(user_year)

    def get_users(self, user_id):

        try:
            info, = self.vkapi.method('users.get',
                                      {'user_id': user_id,
                                       'fields': 'city,bdate,sex,relation'
                                      }
                                      )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if
                     'first_name' in info and 'last_name' in info else None,
                     'sex': info.get('sex'),
                     'city': info.get('city')['title'] if info.get('city') is not None else None,
                     'age': self.age(info.get('bdate'))
                    }

        return user_info

    def users_search(self, params, offset):

        try:
            profile_search = self.vkapi.method('users.search',
                                      {
                                       'count': 50,
                                       'offset': offset,
                                       'hometown': params['city'],
                                       'sex': 1 if params['sex'] == 2 else 2,
                                       'has_photo': True,
                                       'age_from': params['age'] - 5,
                                       'age_to': params['age'] + 5
                                       }
                                      )
        except ApiError as e:
            profile_search = []
            print(f'error = {e}')

        result = [{'name': item['first_name'] + ' ' + item['last_name'],
                   'id': item['id']
                   } for item in profile_search['items'] if item['is_closed'] is False
                  ]
        return result

    def get_photo(self, id):

        try:
            user_photo = self.vkapi.method('photos.get',
                                      {
                                       'owner_id': id,
                                       'album_id': 'profile',
                                       'extended': 1
                                     }
                                      )
        except ApiError as e:
            user_photo = {}
            print(f'error = {e}')
        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in user_photo['items']
                  ]
        sort_photo = sorted(result, key=itemgetter('likes', 'comments'))
        for row in sort_photo:
            print(row)
        return result[:3]


if __name__ == '__main__':
    bot = Vkinder(access_token)
    user_id = 195184223
    params = bot.get_users(user_id)
    tools = bot.users_search(params, 20)
    tool = tools.pop()
    pprint(tools)
    photos = bot.get_photo(tool['id'])
    pprint(photos)


































































































