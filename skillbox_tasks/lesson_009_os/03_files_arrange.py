# -*- coding: utf-8 -*-

import os
import time
import shutil
import platform
import zipfile
from pprint import pprint

# Нужно написать скрипт для упорядочивания фотографий (вообще любых файлов)
# Скрипт должен разложить файлы из одной папки по годам и месяцам в другую.
# Например, так:
#   исходная папка
#       icons/cat.jpg
#       icons/man.jpg
#       icons/new_year_01.jpg
#   результирующая папка
#       icons_by_year/2018/05/cat.jpg
#       icons_by_year/2018/05/man.jpg
#       icons_by_year/2017/12/new_year_01.jpg
#
# Входные параметры основной функции: папка для сканирования, целевая папка.
# Имена файлов в процессе работы скрипта не менять, год и месяц взять из времени создания файла.
# Обработчик файлов делать в обьектном стиле - на классах.
#
# Файлы для работы взять из архива icons.zip - раззиповать проводником в папку icons перед написанием кода.
# Имя целевой папки - icons_by_year (тогда она не попадет в коммит)
#
# Пригодятся функции:
#   os.walk
#   os.path.dirname
#   os.path.join
#   os.path.normpath
#   os.path.getmtime
#   time.gmtime
#   os.makedirs
#   shutil.copy2
#
# Чтение документации/гугла по функциям - приветствуется. Как и поиск альтернативных вариантов :)


class FilesArranger:

    def __init__(self, scan_folder, target_folder):
        self.scan_folder = os.path.normpath(scan_folder)
        self.target_folder = target_folder
        self.full_paths_files = []

    def get_paths_files(self, show_process=False):
        if show_process:
            print('Приветствую тебя', platform.node(), '- cчастливый обладатель ОС ',
                  platform.system() + ' ' + platform.release(),
                  '\nПолучаю имена файлов... \n')
        for dirpath, dirnames, filenames in os.walk(self.scan_folder):
            for file in filenames:
                full_file_path = os.path.join(dirpath, file)
                self.full_paths_files.append(full_file_path)
        if show_process:
            pprint(self.full_paths_files)

    def arrange(self, show_process=False):
        count = 0
        if show_process:
            print('\nНачинаю копирование файлов...\nID процесса -', os.getpid(), '\n')
        for file in self.full_paths_files:
            secs = os.path.getmtime(file)
            file_time = time.gmtime(secs)
            target_folder = os.path.join(self.target_folder, str(file_time[0]), str(file_time[1]))
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            shutil.copy2(file, target_folder)
            if show_process:
                count += 1
                print('File №', count, 'copied')
        print('Excellent!')


class ZipFileArranger:

    def __init__(self, scan_zip_file, target_folder):
        self.scan_file = zipfile.ZipFile(scan_zip_file, 'r')
        self.target_folder = os.path.normpath(target_folder)

    def arrange(self):
        for file in self.scan_file.filelist:
            if file.file_size > 0:
                filename = os.path.basename(file.filename)
                target_folder = os.path.join(self.target_folder, str(file.date_time[0]), str(file.date_time[1]))
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                source = self.scan_file.open(file)
                target = open(os.path.join(target_folder, filename), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)


path = './icons/'
destination_folder = './icons_by_year/'
zip_file_name = 'icons.zip'

# file_arranger = FilesArranger(scan_folder=path, target_folder=destination_folder)
# file_arranger.get_paths_files(show_process=True)
# file_arranger.arrange(show_process=True)
zipper = ZipFileArranger(scan_zip_file=zip_file_name, target_folder=destination_folder)
zipper.arrange()


# # Усложненное задание (делать по желанию)
# Нужно обрабатывать zip-файл, содержащий фотографии, без предварительного извлечения файлов в папку.
# Основная функция должна брать параметром имя zip-файла и имя целевой папки.

# основное и усложненное - зачет!
