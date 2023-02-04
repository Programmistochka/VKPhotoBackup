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
        print(f"Инициализация класса: {self.id}")
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_user_profile_photo_list(self, owner_id, q = 5):
        """Метод получения списка photo_url+likes.count из профиля пользователя VK"""
        url = self.base_url + 'photos.get'
        #print(url)
        #print(f'Owner_id:  {owner_id}')
        params = {'owner_id': f'{owner_id}', 'album_id': 'profile', 'extended': '1'} #extend - расширяет кол-во выдаваемых в ответе полей(для определения лайков)
        res = requests.get(url, params={**self.params, **params}).json()
        #pprint(res)
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
        return response.json()['href']

    def upload_photos_from_vk(self, photo_list, ya_path):
        """Метод загружает фото из интернета на яндекс диск"""
        ya_url = 'v1/disk/resources/upload/'
        request_url = self.base_host + ya_url
        likes_list = [photo_list[n]['likes'] for n in range(0, len(photo_list))]
        for el in photo_list:
            if likes_list.count(el['likes']) == 1:
                el_path = ya_path + str(el['likes']) + '.jpg'
            else:
                el_path = ya_path + str(el['likes']) + '_' + str(el['date']) + '.jpg' 
            params = {'url': el['url_max_photo_size'], 'path': el_path}
            response = requests.post(request_url, params=params, headers = self.get_headers())
            print('---'*30)
            if response.status_code == 202:
                print(f'Фото {el["photo_id"]} загружено на Яндекс.Диск в каталог {el_path}')
        return response.json()

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

    # Получение списка фотографий с атрибутами (photo_id, date, likes, url_max_photo_size)
    profile_photo_list = (vk.get_user_profile_photo_list(owner_id))
    log.write_event(datetime.now(), 'Сформирован список фотографий с параметрами (photo_id, date, likes, url_max_photo_size)')
    log.write_event(datetime.now(), f'photo list:\n{str(vk.get_user_profile_photo_list(owner_id))}')
    
    # Запрос у пользователя количества фотографий, которые необходимо сохранить
    print (f'Всего в профиле пользователя {len(profile_photo_list)} фото')
    q_photos = input('Укажите сколько из них необходимо сохранить на яндекс_Диск: ')
    profile_photo_list = profile_photo_list[0:int(q_photos)]
    pprint(profile_photo_list)
    log.write_event(datetime.now(), f'Пользователь выбрал для сохранения {q_photos} фото')

    # Получить токен для Яндекс.полигон от пользователя 
    ya_token = input('Введите токен для Яндекс.Полигон: ')
    uploader = Yandex(ya_token)
    log.write_event(datetime.now(), 'Авторизация в Яндекс.Полигон.')

    # Загрузка выбранного количества из списка фотографий
    uploader.upload_photos_from_vk(profile_photo_list, '/VK_Photos/')
    log.write_event(datetime.now(), f'Загружено {q_photos} фото из профиля пользователя {owner_id} VK на Яндекс.Диск.')