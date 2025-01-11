import requests
import os
import json
import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_folder(token, folder_name):
    url = f"https://cloud-api.yandex.net/v1/disk/resources/"
    params = {"path": folder_name}
    headers = {'Authorization': f'OAuth {token}'}

    response = requests.put(url, headers=headers, params=params)

    if response.status_code == 201:
        logging.info(f"Папка '{folder_name}' успешно создана.")
    elif response.status_code == 409:
        logging.warning(f"Папка '{folder_name}' уже существует.")
    else:
        logging.error(f"Ошибка при создании папки: {response.status_code}")
        raise Exception("Ошибка создания папки")


def upload_to_yandex_disk(token, folder_name, file_name, file_path):
    headers = {
        'Authorization': f'OAuth {token}',
    }
    url = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path={folder_name}/{file_name}&overwrite=true'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        upload_url = response.json().get('href')
        with open(file_path, 'rb') as file:
            response = requests.put(upload_url, data=file)
            if response.status_code == 201:
                logging.info(f"Файл '{file_name}' успешно загружен.")
            else:
                logging.error(f"Ошибка загрузки файла '{file_name}': {response.status_code}")
    else:
        logging.error("Ошибка получения URL для загрузки:", response.status_code)


def main():
    user_id = input("Введите ID пользователя VK: ")
    token = input("Введите токен Яндекс.Диска: ")
    folder_name = "VK_Photos"
    num_photos = 5

    create_folder(token, folder_name)

    url = 'https://api.vk.com/method/photos.get'
    params = {
        'access_token': token,
        'owner_id': user_id,
        'album_id': 'wall',
        'count': 200,
        'v': '5.131'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'response' in data:
            photos = data['response']['items']

            photos = sorted(photos, key=lambda x: (x['width'] * x['height']), reverse=True)
            top_photos = photos[:num_photos]

            for photo in tqdm(top_photos, desc="Загрузка фотографий"):
                file_name = f"{photo['id']}.jpg"
                file_path = photo['sizes'][-1]['url']

                photo_response = requests.get(file_path)
                if photo_response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(photo_response.content)

                    upload_to_yandex_disk(token, folder_name, file_name, file_name)
                    os.remove(file_name)
                else:
                    logging.error(f"Ошибка скачивания фотографии ID {photo['id']}: {photo_response.status_code}")
        else:
            logging.error("Ошибка в ответе VK API.")
    else:
        logging.error("Ошибка при получении фотографий из VK:", response.status_code)


if __name__ == "__main__":
    main()