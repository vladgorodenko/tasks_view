# -*- coding: utf-8 -*-


# Задача: вычислить 3 тикера с максимальной и 3 тикера с минимальной волатильностью в МНОГОПРОЦЕССНОМ стиле
#
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
# TODO Внимание! это задание можно выполнять только после зачета lesson_012/02_volatility_with_threads.py !!!

import multiprocessing

import os
from functools import reduce
import csv
from queue import Empty

def get_min_max(prev, cur):
    min_price = cur if prev[0] is None else prev[0]
    max_price = cur if prev[1] is None else prev[1]
    if cur > max_price:
        max_price = cur
    if cur < min_price:
        min_price = cur
    return min_price, max_price


class VolatilityCalculator(multiprocessing.Process):

    def __init__(self, filename, queue, *args, **kwargs):
        super(VolatilityCalculator, self).__init__(*args, **kwargs)
        self.source_file = filename
        self.queue = queue

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
        self.queue.put((ticker_name, volatility))


class VolatilityClassifier:

    def __init__(self, folder):
        self.scan_folder = folder
        self.tickers = []
        self.queue = multiprocessing.Queue(maxsize=10)

    def _get_files(self):
        for dirpath, dirnames, filenames in os.walk(self.scan_folder):
            for file in filenames:
                yield os.path.join(dirpath, file)

    def _get_statistic(self):
        volatilities = []
        zeros = []
        calculators = [VolatilityCalculator(filename=file, queue=self.queue)
                       for file in self._get_files()]
        for calculator in calculators:
            calculator.start()

        while True:
            try:
                self.tickers.append(self.queue.get(timeout=5))
            except Empty:
                if not any(calculator.is_alive() for calculator in calculators):
                    break

        for calculator in calculators:
            calculator.join()

        for ticker, volatility in self.tickers:
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
# зачет!
