import requests
from pprint import pprint
from datetime import datetime
import os

class VK:
    
    base_url = 'https://api.vk.com/method/'

    def __init__(self, access_token, user_id, version='5.131'):
        """Метод инициализации класса VK"""
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        """Метод вывода информации о пользователе по запросу users.get"""
        url = self.base_url + 'users.get'
        print('-'*10)
        print(url)
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_user_profile_photo(self):
        """Метод получения фото из профиля пользователя VK"""
        url = self.base_url + 'photos.get'
        print('-'*10)
        print(url)
        params = {'album_id': 'profile'}
        res = requests.get(url, params={**self.params, **params}).json()
        photos = list(res['response']['items'][0]['sizes'])
        print('_________')
        print('_________')
        pprint(res)
        print('_________')
        print('_________')
        dict_photos = {photos[el]['url']:photos[el]['height'] for el in range(1, len(photos))}
        print(max(dict_photos))
        return max(dict_photos)

class Yandex:
    
    base_host = "https://cloud-api.yandex.net:443/"
    
    def __init__(self, token: str):
        """Метод инициализации класса Yandex"""
        self.token = token
    
    def get_headers(self):
        """Метод для передачи заголовков"""
        return {
            'Content_Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
    
    def _get_upload_link(self, path):
        """Метод для получения ссылки для загрузки"""
        url = '/v1/disk/resources/upload/'
        request_url = self.base_host + url
        params = {'path': path, 'overwrite': True}
        response = requests.get(request_url, headers = self.get_headers(), params = params)
        #print(response.status_code)
        return response.json()['href']

    def upload(self, file_path: str, yandex_path):
        """Метод загружает файл с локального компа на яндекс диск"""
        upload_url = self._get_upload_link(yandex_path)
        response = requests.put(upload_url, data=open(file_path, 'rb'), headers = self.get_headers())
        if response.status_code == 201:
            print('Загрузка прошла успешно')

    def upload_from_vk(self, url, ya_path):
        """Метод загружает фото из интернета на яндекс диск"""
        print('________________________')
        ya_url = 'v1/disk/resources/upload/'
        request_url = self.base_host + ya_url
        print(f'request_url: {request_url}')
        print(f'url: {url}')
        print(f'ya_path: {ya_path}')
        #url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/A_rose_flower.jpg/220px-A_rose_flower.jpg'
        params = {'url': url, 'path': ya_path}

        response = requests.post(request_url, params=params, headers = self.get_headers())
        print('________________________')
        print(response.status_code)
        pprint(response.json())
        return response

class Log:

    full_path = ''

    def __init__(self, start_date_time):
        """Метод инициализации класса Log"""
        start_time = str(start_date_time)
        file_time = start_time[0:10].replace('-','') + '_' + start_time[11:19].replace(':','-') 
        # Определение пути сохранения файла с логами
        logfile_name = 'log_' + file_time + '.txt'
        current_path = os.getcwd() 
        folder_name = 'logs'
        self.full_path = os.path.join(current_path, folder_name, logfile_name)
        with open(self.full_path, 'x') as f:
            f.write(f'{start_time[0:19]} Запуск програмы. Создание и сохранение лог-файла в каталоге {self.full_path}\n')
        print(f'Лог-файл {logfile_name} создан')

    def write_event(self, date_time, event: str):
        """Метод записи события в лог-файл"""
        date_time_event = str(date_time)
        with open(self.full_path, 'a') as f:
            f.write(f'{date_time_event[0:19]} {event}\n') 
       
        
if __name__ == '__main__':
    # Создание экземпляра класса Log для записи действий программы в лог-файл
    log = Log(datetime.now())
    # Получить токен vk и id пользователя из файла Settings_vk.txt 
    with open('Settings_vk.txt', 'rt', encoding='utf-8') as file:
        user_id = file.readline()
        vk_token = file.readline()
    log.write_event(datetime.now(), 'Загружен токен и user ID для VK.')

    vk = VK(vk_token, user_id)
    log.write_event(datetime.now(), 'Авторизация в сервисах VK.')
    #print(vk.users_info())
    pprint(vk.get_user_profile_photo())

    # Получить токен для Яндекс.полигон из файла Settings_ya.txt 
    with open('Settings_ya.txt', 'rt', encoding='utf-8') as file:
        ya_token = file.readline()
    log.write_event(datetime.now(), 'Загружен токен для Яндекс.Полигон.')
    
    uploader = Yandex(ya_token)
    log.write_event(datetime.now(), 'Авторизация в Яндекс.Полигон.')
    #print(uploader.upload('star.jpg', '/VK_Photos/New.jpg'))
    uploader.upload_from_vk(vk.get_user_profile_photo(), '/VK_Photos/New.jpg')
    log.write_event(datetime.now(), 'Загрузка фото из профиля пользователя VK на Яндекс.Диск.')

    print("__________________")