# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import cv2
from PIL import Image, ImageDraw, ImageFont
from lesson_016 import weather_db as db
import peewee
from datetime import datetime, date, timedelta


BACKGROUNDS = {
      "Малооблачно": "04.jpeg",
      "Снег": "01.jpeg",
      "Небольшой снег": "05.jpeg",
      "Облачно с прояснениями": "06.jpeg",
      "Ясно": "08.jpeg",
      "Пасмурно": "07.jpeg",
      "Дождь": "02.jpeg"
}

ICONS = {
      "Малооблачно": "cloud.png",
      "Снег": "snow.png",
      "Небольшой снег": "snow.png",
      "Облачно с прояснениями": "cloud.png",
      "Ясно": "sunny.png",
      "Пасмурно": "umbrella.png",
      "Дождь": "umbrella.png"
}


class DateTimeWorker:

    def __init__(self):
        pass

    @staticmethod
    def create_range_of_dates(start_date=date.today(), end_date=date.today() + timedelta(1)):
        range_of_dates = []
        days_number = end_date - start_date
        for i in range(days_number.days):
            temp_date = date.strftime(start_date + timedelta(i), '%Y-%m-%d')
            range_of_dates.append(temp_date)
        return range_of_dates


class YandexWeatherParser:
    """
   Генератор погоды посредством парсера

   :param city: город

   :return weather_in_dates: список погод(словарей) на даты 3 дня до и 30 дней после "сегодня"
   """

    def __init__(self, city='moscow'):
        self.city = city
        self.weather_in_dates = []

    def get_weather(self):
        weather_page = requests.get(f'https://yandex.ru/pogoda/{self.city}')
        html_text = BeautifulSoup(weather_page.text, features='html.parser')
        weather_container = html_text.find_all('div', class_='forecast-briefly__day')
        for weather_card in weather_container:
            date = weather_card.find('time')
            temperatures = [temperature.text for temperature in weather_card.find_all('span', class_='temp__value')]
            status = weather_card.find('div', class_='forecast-briefly__condition')
            day_weather = {'source': self.__class__.__name__,
                           'city': self.city,
                           'date': re.search(r'(\d+-\d+-\d+)', date.attrs['datetime']).group(1),
                           't_day': temperatures[0],
                           't_night': temperatures[1],
                           'weather_status': status.text}
            self.weather_in_dates.append(day_weather)
        return self.weather_in_dates


class WeatherMaker:
    """
    Генератор погоды посредством парсера

    :param city: город
    :param range_dates: список с датами

    :return weather: погода на дату
    """

    def __init__(self, city='moscow', range_dates=None):
        self.range_dates = range_dates
        self.city = city
        self.weather_parser = YandexWeatherParser(self.city)

    def get_weather_from_source(self):
        weather_in_days = self.weather_parser.get_weather()
        for weather in weather_in_days:
            yield weather


class ImageMaker:
    """
        Создание постера и вывод на экран

        :param weather_data: погода

        """

    def __init__(self, weather_data):
        self.weather = weather_data

    def view_image(self, image, name_of_window):
        cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
        cv2.imshow(name_of_window, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def create_weather_banner(self):  # cv2.putText не работает с русскими символами?
        font = ImageFont.truetype('./images/Roboto-Bold.ttf', size=30)
        weather_image = Image.open('./images/probe3.png')

        draw = ImageDraw.Draw(weather_image)
        (x, y) = (150, 350)
        # Выглядит ужасно конечно, но пока так сойдет
        message = f"Погода в {DatabaseUpdater.get_ru_city(self.weather['city'])} \n\n" \
                  f"на {self.weather['date']} \n\n" \
                  f"Днём:   {self.weather['t_day']}\n" \
                  f"Ночью: {self.weather['t_night']}\n\n" \
                  f"{self.weather['weather_status']}"

        color = 'rgb(0,0,0)'
        draw.text((x, y), message, fill=color, font=font)
        del draw
        icon_filename = ICONS[self.weather["weather_status"]]
        icon = Image.open(f'./images/icons/{icon_filename}')
        icon = icon.resize((150, 150), Image.ANTIALIAS)
        weather_image.alpha_composite(icon, (400, 450))

        banner_path = './images/weather_banner.png'
        weather_image.save(banner_path,)

        return banner_path

    @staticmethod
    def draw_gradient(background_image):
        height, width = background_image.shape[:2]
        grad, delta = 0, 255 / width
        for i in range(height):
            for j in range(width):
                background_image[i, j] = (grad, 0, grad)

                grad += delta
            grad = 0
        return background_image

    def create_poster(self):

        bg_filename = BACKGROUNDS[self.weather["weather_status"]]
        background = cv2.imread(f'./images/backgrounds/{bg_filename}')
        background = cv2.GaussianBlur(background, (9, 11), 0)
        background = background[0:1067, 400:1000]
        background = self.draw_gradient(background)
        inner_banner = cv2.imread(self.create_weather_banner())

        weather_poster = cv2.addWeighted(background, 0.3, inner_banner, 0.7, 2)
        cv2.imwrite(f'./images/weather_poster_{self.weather["date"]}.jpg', weather_poster)
        self.view_image(weather_poster, 'weather')


class DatabaseUpdater:

    def __init__(self, database_name):
        self.database_name = peewee.SqliteDatabase(database_name)

    def initialize(self):
        db.database_proxy.initialize(self.database_name)
        db.database_proxy.create_tables([db.WeatherJournal, db.Cities])

    @staticmethod
    def get_ru_city(city_en):
        return db.Cities.select(db.Cities.city_ru_pp).where(db.Cities.city_en == city_en).dicts()[0]['city_ru_pp']

    @staticmethod
    def get_en_city(city_ru):
        return db.Cities.select(db.Cities.city_en).where(db.Cities.city_ru == city_ru).dicts()[0]['city_en']

    @staticmethod
    def get_weather(city, range_of_dates):
        weather_predict = db.WeatherJournal.select(
            db.WeatherJournal.city,
            db.Cities.city_ru_pp,
            db.WeatherJournal.date,
            db.WeatherJournal.t_day,
            db.WeatherJournal.t_night,
            db.WeatherJournal.weather_status
        ).join(db.Cities, 'LEFT JOIN', (db.WeatherJournal.city == db.Cities.city_en), db.WeatherJournal). \
            where((db.WeatherJournal.city == city) & (db.WeatherJournal.date.in_(range_of_dates))).distinct().dicts()
        return weather_predict

    @staticmethod
    def insert_weather(weather_data):

        date_rows = db.WeatherJournal.select(db.WeatherJournal.date,
                                             db.WeatherJournal.city,
                                             db.WeatherJournal.source).distinct().dicts()
        actual_data = [row['date'] + '&' + row['city'] + '&' + row['source'] for row in date_rows]
        for input_row in weather_data:
            # для отсуствия дубликатов в базе
            if input_row['date'] + '&' + input_row['city'] + '&' + input_row['source'] in actual_data:
                db.WeatherJournal.update(**input_row)
            else:
                db.WeatherJournal.create(**input_row)


class MyWeather:

    def __init__(self, database_name='weather_data.db', city_name='irkutsk', print_posters=True):
        self.database_name = database_name
        self.city_name = city_name
        self.print_posters = print_posters

        self.main_menu = {
            "1": self.predict_today,
            "2": self.predict_in_dates,
            "3": self.pour_predict,
            "4": self.switch_posterprinting,
            "5": self.change_city,
        }


    def predict_prev_week(self):
        range_dates = DateTimeWorker.create_range_of_dates(date.today() - timedelta(7), date.today())
        print(f'Приветствую тебя! Держи погоду за прошлую неделю в {DatabaseUpdater.get_ru_city(self.city_name)}:')
        query = DatabaseUpdater.get_weather(city=self.city_name, range_of_dates=range_dates)
        for row in query:
            if row is not None:
                print(
                    f'В {row["city_ru_pp"]} на {row["date"]}: {row["weather_status"]}, днём: {row["t_day"]} ночью: {row["t_night"]};')

    def predict_today(self):
        range_dates = DateTimeWorker.create_range_of_dates()
        query = DatabaseUpdater.get_weather(city=self.city_name, range_of_dates=range_dates)
        for row in query:
            if row is not None:
                print(
                    f'Сегодня в {row["city_ru_pp"]}: {row["weather_status"]}, днём: {row["t_day"]} ночью: {row["t_night"]};')
                if self.print_posters:
                    ImageMaker(row).create_poster()

    def predict_in_dates(self):
        start_date = datetime.strptime(input('Введите начальную дату (например: 2020-03-20): '), '%Y-%m-%d')
        end_date = datetime.strptime(input('Введите конечную дату (например: 2020-03-21, не вкл.): '),
                                     '%Y-%m-%d')
        range_dates = DateTimeWorker.create_range_of_dates(start_date, end_date)
        query = DatabaseUpdater.get_weather(city=self.city_name, range_of_dates=range_dates)
        for row in query:
            if row is not None:
                print(
                    f'В {row["city_ru_pp"]} на {row["date"]}: {row["weather_status"]}, днём: {row["t_day"]} ночью: {row["t_night"]};')
                if self.print_posters:
                    ImageMaker(row).create_poster()

    def pour_predict(self):
        weather_data = [weather for weather in WeatherMaker(city=self.city_name).get_weather_from_source()]
        DatabaseUpdater.insert_weather(weather_data)  # Заливка на месяц

    def switch_posterprinting(self):
        self.print_posters = True if self.print_posters is not True else False
        print('Вкл.') if self.print_posters else print('Выкл.')

    def change_city(self):
        self.city_name = input('Введите город (Москва, Иркутск, Чита):').capitalize()
        self.city_name = DatabaseUpdater.get_en_city(self.city_name)

    def run(self):
        DatabaseUpdater(self.database_name).initialize()
        self.predict_prev_week()
        #  Основной цикл:
        while True:

            print("""  
            1. Показать прогноз на сегодня
            2. Показать прогноз за диапазон дат
            3. Залить прогноз в базу
            4. Вкл./откл. печать постеров
            5. Поменять город
                    """)

            choice = input('Выберите действие:')
            self.main_menu.get(choice, exit)()


if __name__ == '__main__':
    MyWeather().run()
