# -*- coding: utf-8 -*-

# Подсчитать статистику по буквам в романе Война и Мир.
# Входные параметры: файл для сканирования
# Статистику считать только для букв алфавита (см функцию .isalpha() для строк)
#
# Вывести на консоль упорядоченную статистику в виде
# +---------+----------+
# |  буква  | частота  |
# +---------+----------+
# |    А    |   77777  |
# |    Б    |   55555  |
# |   ...   |   .....  |
# |    a    |   33333  |
# |    б    |   11111  |
# |   ...   |   .....  |
# +---------+----------+
# |  итого  | 9999999  |
# +---------+----------+
# Ширину таблицы подберите по своему вкусу

import zipfile
import operator


class LetterStatisticCollector:

    def __init__(self, file_name):
        self.file_name = file_name
        self.letters_statistic = {}
        self.total_letters = 0

    def unzip(self):
        zfile = zipfile.ZipFile(self.file_name, 'r')
        for filename in zfile.namelist():
            zfile.extract(filename)
            self.file_name = filename

    def collect(self):
        if self.file_name.endswith('.zip'):
            self.unzip()
        with open(self.file_name, 'r', encoding='cp1251') as file:
            for line in file:
                for char in line:
                    if char.isalpha():
                        self.total_letters += 1
                        if char in self.letters_statistic:
                            self.letters_statistic[char] += 1
                        else:
                            self.letters_statistic[char] = 1

    def print_statistic(self, sorted_statistic=None, output_file_name=None):
        if output_file_name:
            file = open(output_file_name, 'w', encoding='utf8')
        else:
            file = None
        print('+------------+-----------------+', file=file)
        print('|   буква    |      частота    |', file=file)
        print('+------------+-----------------+', file=file)
        if sorted_statistic is None:
            sorted_statistic = self.letters_statistic.items()
        for cuple in sorted_statistic:
            print('|    {}       |     {:7d}     |'.format(cuple[0], cuple[1]), file=file)
        print('+------------+-----------------+', file=file)
        print('|  итого     |     {:7d}     |'.format(self.total_letters), file=file)
        print('+------------+-----------------+', file=file)
        if file:
            file.close()

    def get_sorted_by_alpha(self, reverse=False):
        # А зачем условия? Сразу в функцию sorted делаем reverse=reverse
        # точно, вот блин голова садовая
        sorted_list = sorted(self.letters_statistic.items(), reverse=reverse)
        return sorted_list

    def get_sorted_by_value(self, reverse=False):
        sorted_list = sorted(self.letters_statistic.items(), key=operator.itemgetter(1), reverse=reverse)
        return sorted_list


collector = LetterStatisticCollector(file_name='./python_snippets/voyna-i-mir.txt.zip')
collector.collect()
# sort_list = collector.get_sorted_by_alpha(reverse=False)
sort_list = collector.get_sorted_by_value(reverse=True)
collector.print_statistic(sorted_statistic=sort_list)

# зачет!
