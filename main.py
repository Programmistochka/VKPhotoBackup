import requests
from pprint import pprint
from datetime import datetime
import os

def line(k=30):
    print()
    print('---'*k)


class VK:
    
    base_url = 'https://api.vk.com/method/'

    def __init__(self, access_token, user_id, version='5.131'):
        """Метод инициализации класса VK"""
        self.token = access_token
        self.id = user_id
        print(f"Инициализация класса: {self.id}")
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_user_profile_one_photo(self, owner_id):
        """Метод получения фото из профиля пользователя VK"""
        url = self.base_url + 'photos.get'
        line()
        print(url)
        print(f'owner_id: {owner_id} ')
        params = {'owner_id': f'{owner_id}', 'album_id': 'profile', 'extended': '1'}
        res = requests.get(url, params={**self.params, **params}).json()
        line()
        pprint(res)
        line()
        photos = list(res['response']['items'][0]['sizes'])
        dict_photos = {photos[el]['url']:photos[el]['height'] for el in range(1, len(photos))}
        print(max(dict_photos))
        return max(dict_photos)

    def get_user_profile_photo_list(self, owner_id, q = 5):
        """Метод получения списка photo_url+likes.count из профиля пользователя VK"""
        url = self.base_url + 'photos.get'
        line()
        print(url)
        print(f'Owner_id:  {owner_id}')
        params = {'owner_id': f'{owner_id}', 'album_id': 'profile', 'extended': '1'} #extend - расширяет кол-во выдаваемых в ответе полей(для определения лайков)
        res = requests.get(url, params={**self.params, **params}).json()
        line()
        pprint(res)
        line()
        list_photos=[]
        for item in res['response']['items']:
            ph_date = item['date']
            ph_date = datetime.utcfromtimestamp(ph_date).strftime('%Y-%m-%d_%H-%M-%S') #преобразование времени из unixtime в utc-формат
            
            #поиск url-фото с максимальным размером
            photos = list(item['sizes'])
            dict_photos = {photos[el]['url']:photos[el]['height'] for el in range(1, len(photos))}
            #добавление информации о фотографии в список
            list_photos.append({'photo_id': item['id'],
                                'date': ph_date,
                                'likes': item['likes']['count'],
                                'url_max_photo_size': max(dict_photos)})
        return list_photos
        
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
    
    # Получение токен vk из файла Settings_vk.txt
    with open('Settings_vk.txt', 'rt', encoding='utf-8') as file:
        vk_token = file.readline()
        user_id = file.readline()
    log.write_event(datetime.now(), 'Загружен токен и user ID для VK из файла Settings_vk.txt')
    
    # Запрос информации от пользователя (user_id)
    owner_id = input("Введите user_id для VK пользователя, у которого необходимо скопировать фото: ")
    log.write_event(datetime.now(), f'От пользователя получен owner_id: {owner_id}')

    # Создание экземпляра класса VK, для получения фотографий
    vk = VK(vk_token, user_id)
    log.write_event(datetime.now(), 'Авторизация в сервисах VK.')

    #Получение списка фотографий с атрибутами (photo_id, date, likes, url_max_photo_size)
    print("________________GET__Q_PHOTOS___________________")
    pprint(vk.get_user_profile_photo_list(owner_id))

    # Получить токен для Яндекс.полигон из файла Settings_ya.txt 
    with open('Settings_ya.txt', 'rt', encoding='utf-8') as file:
        ya_token = file.readline()
    log.write_event(datetime.now(), 'Загружен токен для Яндекс.Полигон из файла Settings_ya.txt')
    
    uploader = Yandex(ya_token)
    log.write_event(datetime.now(), 'Авторизация в Яндекс.Полигон.')
    #print(uploader.upload('star.jpg', '/VK_Photos/New.jpg'))
    uploader.upload_from_vk(vk.get_user_profile_one_photo(owner_id), '/VK_Photos/New.jpg')
    log.write_event(datetime.now(), f'Загрузка фото из профиля пользователя {owner_id} VK на Яндекс.Диск.')

    print("__________________")