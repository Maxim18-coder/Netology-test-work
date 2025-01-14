import requests
import os
import json
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class VKApi:
    def __init__(self, token):
        self.token = token
        self.version = '5.131'

    def get_photos(self, user_id=None, screen_name=None):
        base_url = 'https://api.vk.com/method/photos.getAll'
        params = {
            'access_token': self.token,
            'v': self.version,
            'owner_id': user_id,
            'count': 5
        }

        if screen_name:
            user_info = self.get_user_info(screen_name)
            if user_info:
                params['owner_id'] = user_info['id']

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json().get('response', {}).get('items', [])
        else:
            logging.error(f"Ошибка при получении фотографий: {response.text}")
            return []

    def get_user_info(self, screen_name):
        base_url = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': screen_name,
            'access_token': self.token,
            'v': self.version
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json().get('response', [{}])[0]
        else:
            logging.error(f"Ошибка получения информации о пользователе: {response.text}")
            return None


class YandexDisk:
    def __init__(self, token):
        self.token = token

    def create_folder(self, folder_name):
        url = f"https://cloud-api.yandex.net/v1/disk/resources/"
        params = {"path": folder_name}
        headers = {'Authorization': f'OAuth {self.token}'}

        response = requests.put(url, headers=headers, params=params)

        if response.status_code == 201:
            logging.info(f"Папка '{folder_name}' успешно создана.")
        elif response.status_code == 409:
            logging.warning(f"Папка '{folder_name}' уже существует.")
        else:
            logging.error(f"Ошибка при создании папки: {response.text}")

    def upload_photo(self, photo_data, folder_name):
        url = f"https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {'Authorization': f'OAuth {self.token}'}
        params = {
            "path": f"{folder_name}/{photo_data['likes']['count']}_"
                    f"{photo_data['date']}.jpg" if photo_data['likes'][
                                                       'count'] == 0 else f"{photo_data['likes']['count']}.jpg",
            "overwrite": "true"
        }

        upload_link_response = requests.get(url, headers=headers, params=params)
        upload_link_response.raise_for_status()
        upload_url = upload_link_response.json()['href']

        photo_url = photo_data['sizes'][-1]['url']
        response = requests.get(photo_url, stream=True)

        if response.status_code == 200:
            with requests.put(upload_url, files={'file': response.raw}) as upload_res:
                if upload_res.status_code == 201:
                    logging.info(f"Фото '{photo_data['likes']['count']}.jpg' загружено успешно.")
                else:
                    logging.error(f"Ошибка при загрузке фотографии: {upload_res.text}")
        else:
            logging.error(f"Ошибка при получении фото: {response.text}")


def main():
    vk_token = input("Введите токен VK: ")
    yandex_token = input("Введите токен Яндекс.Диска: ")
    user_input = input("Введите ID или screen_name пользователя: ")

    vk_api = VKApi(vk_token)
    yandex_disk = YandexDisk(yandex_token)

    photos = vk_api.get_photos(screen_name=user_input)

    folder_name = 'VK_Photos'
    yandex_disk.create_folder(folder_name)

    for photo in tqdm(photos, desc="Загрузка фотографий"):
        yandex_disk.upload_photo(photo, folder_name)


if __name__ == '__main__':
    main()