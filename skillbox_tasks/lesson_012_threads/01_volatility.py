# -*- coding: utf-8 -*-


# Описание предметной области:
#
# При торгах на бирже совершаются сделки - один купил, второй продал.
# Покупают и продают ценные бумаги (акции, облигации, фьючерсы, етс). Ценные бумаги - это по сути долговые расписки.
# Ценные бумаги выпускаются партиями, от десятка до несколько миллионов штук.
# Каждая такая партия (выпуск) имеет свой торговый код на бирже - тикер - https://goo.gl/MJQ5Lq
# Все бумаги из этой партии (выпуска) одинаковы в цене, поэтому говорят о цене одной бумаги.
# У разных выпусков бумаг - разные цены, которые могут отличаться в сотни и тысячи раз.
# Каждая биржевая сделка характеризуется:
#   тикер ценнной бумаги
#   время сделки
#   цена сделки
#   обьем сделки (сколько ценных бумаг было куплено)
#
# В ходе торгов цены сделок могут со временем расти и понижаться. Величина изменения цен называтея волатильностью.
# Например, если бумага №1 торговалась с ценами 11, 11, 12, 11, 12, 11, 11, 11 - то она мало волатильна.
# А если у бумаги №2 цены сделок были: 20, 15, 23, 56, 100, 50, 3, 10 - то такая бумага имеет большую волатильность.
# Волатильность можно считать разными способами, мы будем считать сильно упрощенным способом -
# отклонение в процентах от средней цены за торговую сессию:
#   средняя цена = (максимальная цена + минимальная цена) / 2
#   волатильность = ((максимальная цена - минимальная цена) / средняя цена) * 100%
# Например для бумаги №1:
#   average_price = (12 + 11) / 2 = 11.5
#   volatility = ((12 - 11) / average_price) * 100 = 8.7%
# Для бумаги №2:
#   average_price = (100 + 3) / 2 = 51.5
#   volatility = ((100 - 3) / average_price) * 100 = 188.34%
#
# В реальности волатильность рассчитывается так: https://goo.gl/VJNmmY
#
# Задача: вычислить 3 тикера с максимальной и 3 тикера с минимальной волатильностью.
# Бумаги с нулевой волатильностью вывести отдельно.
# Результаты вывести на консоль в виде:
#   Максимальная волатильность:
#       ТИКЕР1 - ХХХ.ХХ %
#       ТИКЕР2 - ХХХ.ХХ %
#       ТИКЕР3 - ХХХ.ХХ %
#   Минимальная волатильность:
#       ТИКЕР4 - ХХХ.ХХ %
#       ТИКЕР5 - ХХХ.ХХ %
#       ТИКЕР6 - ХХХ.ХХ %
#   Нулевая волатильность:
#       ТИКЕР7, ТИКЕР8, ТИКЕР9, ТИКЕР10, ТИКЕР11, ТИКЕР12
# Волатильности указывать в порядке убывания. Тикеры с нулевой волатильностью упорядочить по имени.
#
# Подготовка исходных данных
# 1. Скачать файл https://drive.google.com/file/d/1l5sia-9c-t91iIPiGyBc1s9mQ8RgTNqb/view?usp=sharing
#       (обратите внимание на значок скачивания в правом верхнем углу,
#       см https://drive.google.com/file/d/1M6mW1jI2RdZhdSCEmlbFi5eoAXOR3u6G/view?usp=sharing)
# 2. Раззиповать средствами операционной системы содержимое архива
#       в папку python_base_source/lesson_012/trades
# 3. В каждом файле в папке trades содержится данные по сделакам по одному тикеру, разделенные запятыми.
#   Первая строка - название колонок:
#       SECID - тикер
#       TRADETIME - время сделки
#       PRICE - цена сделки
#       QUANTITY - количество бумаг в этой сделке
#   Все последующие строки в файле - данные о сделках
#
# Подсказка: нужно последовательно открывать каждый файл, вычитывать данные, высчитывать волатильность и запоминать.
# Вывод на консоль можно сделать только после обработки всех файлов.

import os
from functools import reduce
import csv


def get_min_max(prev, cur):  #
    min_price = cur if prev[0] is None else prev[0]
    max_price = cur if prev[1] is None else prev[1]
    if cur > max_price:
        max_price = cur
    if cur < min_price:
        min_price = cur
    return min_price, max_price


class VolatilityCalculator:

    def __init__(self, filename):
        self.source_file = filename

    def run(self):
        with open(self.source_file, 'r') as file:
            file.readline()
            ticker_name = file.read(4)
            reader = csv.reader(file)
            min_price, max_price = reduce(get_min_max, (float(line[2]) for line in reader), [None, None])
            if min_price is None or max_price is None:
                volatility = 0
            else:
                average_price = (min_price + max_price) / 2
                volatility = ((max_price - min_price) / average_price) * 100
            return ticker_name, volatility


class VolatilityClassifier:

    def __init__(self, folder):
        self.scan_folder = folder

    def _get_files(self):
        for dirpath, dirnames, filenames in os.walk(self.scan_folder):
            for file in filenames:
                yield os.path.join(dirpath, file)

    def _get_statistic(self):
        volatilities = []
        zeros = []
        calculators = [VolatilityCalculator(filename=file).run() for file in self._get_files()]
        for ticker, volatility in calculators:
            if volatility == 0:
                zeros.append((ticker, volatility))
            else:
                volatilities.append((ticker, volatility))

        return volatilities, zeros

    def to_classify(self):
        valid_tickers, zeros_tickers = self._get_statistic()
        valid_tickers.sort(key=lambda vol: vol[1])
        zeros_tickers.sort()
        print('Максимальная волатильность:')

        for ticker, volatility in valid_tickers[:-4:-1]:
            print(f'    {ticker} - {volatility:.2f} %')

        print('Минимальная волатильность:')
        for ticker, volatility in reversed(valid_tickers[:3]):
            print(f'    {ticker} - {volatility:.2f} %')

        print('Нулевая волатильность:')
        print(', '.join(ticker[0] for ticker in zeros_tickers))


if __name__ == '__main__':
    scan_folder = os.path.normpath('../../python_base_source/lesson_012/trades')
    volatility_counter = VolatilityClassifier(folder=scan_folder)
    volatility_counter.to_classify()

# зачет, join может работать и с генератором - нет смысла создавать лист, да ticker[0] это уже строка
# также стоит разобраться с пустым первым значением, чтобы в след. части эта проблема не повторялась
# , CLM9, CYH9, EDU9, EuH0, EuZ9, JPM9, MTM9, O4H9, PDU9, PTU9, RIH0, RRG9, TRH9, VIH9

# Что не так? У меня выводит нормально - первое значение не пустое
