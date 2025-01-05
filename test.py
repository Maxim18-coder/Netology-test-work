import requests

token = 
user_id = '502402141'
album_id = 'wall_id'

url = 'https://api.vk.com/method/photos.get'
params = {
    'access_token': token,
    'owner_id': user_id,
    'album_id': album_id,
    'v': '5.131'
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    if 'response' in data:
        photos = data['response']['items']
        for photo in photos:
            print(f"ID: {photo['id']}, Фото URL: {photo['sizes'][-1]['url']}")
    else:
        print("Ошибка:", data.get('error', {}).get('error_msg', 'Неизвестная ошибка'))
else:
    print("Ошибка запроса:", response.status_code)

# class VK:
#     def __init__(self, access_token, user_id, version='5.131'):
#         self.token = access_token
#         self.id = user_id
#         self.version = version
#         self.params = {'access_token': self.token, 'v':
#     self.version}
#
#     def users_info(self):
#         url = 'https://api.vk.com/method/users.get'
#         params = {'user_ids': self.id}
#         response = requests.get(url, params=params)
#         return response.json()


# vk = VK(access_token, user_id)
# print(vk.users_info())