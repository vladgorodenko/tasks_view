# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет две локации и один монстр
# (то есть в коренном json-объекте содержится список, содержащий два json-объекта, одного монстра и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в рассчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом рискует никогда не найти путь.
#
# Также, при каждом ходе игрока ваш скрипт должен запоминать следущую информацию:
# - текущую локацию
# - текущее количество опыта
# - текущие дату и время (для этого используйте библиотеку datetime)
# После успешного или неуспешного завершения игры вам необходимо записать
# всю собранную информацию в csv файл dungeon.csv.
# Названия столбцов для csv файла: current_location, current_experience, current_date
#
#
# Пример взаимодействия с игроком:
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло времени: 00:00
#
# Внутри вы видите:
# — Вход в локацию: Location_1_tm1040
# — Вход в локацию: Location_2_tm123456
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали переход в локацию Location_2_tm1234567890
#
# Вы находитесь в Location_2_tm1234567890
# У вас 0 опыта и осталось 0.0987654321 секунд до наводнения
# Прошло времени: 20:00
#
# Внутри вы видите:
# — Монстра Mob_exp10_tm10
# — Вход в локацию: Location_3_tm55500
# — Вход в локацию: Location_4_tm66600
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали сражаться с монстром
#
# Вы находитесь в Location_2_tm0
# У вас 10 опыта и осталось -9.9012345679 секунд до наводнения
#
# Вы не успели открыть люк!!! НАВОДНЕНИЕ!!! Алярм!
#
# У вас темнеет в глазах... прощай, принцесса...
# Но что это?! Вы воскресли у входа в пещеру... Не зря матушка дала вам оберег :)
# Ну, на этот-то раз у вас все получится! Трепещите, монстры!
# Вы осторожно входите в пещеру... (текст умирания/воскрешения можно придумать свой ;)
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло уже 0:00:00
# Внутри вы видите:
#  ...
#  ...
#
# и так далее...
import csv
import json
import datetime
import time
from decimal import Decimal
import re
from termcolor import cprint


class GameQuitException(Exception):
    pass


class GameOverException(Exception):
    pass


def parse_json_map(rpg_json_map):
    with open(rpg_json_map, 'r') as json_file:
        json_data = json.load(json_file)
    return json_data


def game_over_fairy_tail():
    filepath = '.\\game_text_maintenance\\game_over.txt'
    with open(filepath, 'r') as textfile:
        usual_text = textfile.read()
    return usual_text

# Учитывая время и опыт, не забывайте о точности вычислений!


def write_statistic(field_names, field_values, csv_filepath):
    statistic = {}
    for i in range(len(field_names)):
        statistic[field_names[i]] = field_values[i]
    with open(csv_filepath, 'a', newline='') as out_csv:
        writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=field_names, )
        writer.writerows([statistic])


class Game:

    def __init__(self, rpg_json_map, game_time, experience_for_win):
        self.rpg_map = parse_json_map(rpg_json_map)
        self.remaining_timer = Decimal(game_time)
        self.experience_for_win = experience_for_win


class Hero:

    def __init__(self):
        self.current_experience = 0

        self.game_timer = Decimal(0)
        self.time_elapsed = None
        self.current_date = datetime.datetime.now()

        self.current_location = None

        self.current_npc = []
        self.new_locations = []
        self.new_locations_names = []

    def inspect_map(self, rpg_map):
        self.new_locations.clear()
        self.new_locations_names.clear()
        self.current_npc.clear()

        for key, entities in rpg_map.items():
            self.current_location = key
            for entity in entities:
                if isinstance(entity, dict):
                    self.new_locations.append(entity)
                    self.new_locations_names.append(','.join(entity))
                elif isinstance(entity, str):
                    self.current_npc.append(entity)

    def inspect_current_location(self):

        # print(new_locations_names, current_npc)
        print('\nВнутри вы видите:')
        for npc in self.current_npc:
            print(f'- {npc}')
        for location_name in self.new_locations_names:
            print(f'- {location_name}')

    def kill_npc(self):
        if not len(self.current_npc):
            print('Очнись, вокруг никого...\n')
            return
        print('Какого монстра ты хочешь убить:')
        for i, npc in enumerate(self.current_npc):
            print(f'{i+1}) {npc}')

        try:
            choice = int(input())
            choice = choice-1 if choice else None
            killed_npc = self.current_npc.pop(choice)
        except Exception:
            raise IndexError('Стоит точнее целиться - монстры не дремлют... Этот промах стоил тебе жизни\n')

        earned_exp = int(re.search(r'exp(\d+)', killed_npc).group(1))
        spent_time = Decimal(re.search(r'tm(\d+\.?\d*)', killed_npc).group(1))
        self.current_experience += earned_exp
        self.game_timer += spent_time

        cprint(f'Одним взмахом руки вы убиваете монстра "{killed_npc}" за {spent_time} секунд '
               f'и получаете {earned_exp} ед. опыта', 'cyan')



    def select_new_location(self):
        mapping_location = []
        print('В какую локацию вы хотите перейти?')

        for i, location in enumerate(self.new_locations_names):
            print(f'{i+1}) {location}')
            mapping_location.append(location)

        try:
            choice = int(input())
            choice = choice - 1 if choice else None
            selected_new_location = mapping_location.pop(choice)
        except Exception:
            raise IndexError('Попытка пролезть в скрытую локацию не увенчалась успехом - вас придавило булыжником :(')



        spent_time = Decimal(re.search(r'tm(\d+\.?\d*)', selected_new_location).group(1))
        self.game_timer += spent_time

        for new_location in self.new_locations:
            if selected_new_location in new_location:  # так поиск будет быстрее
                new_map = new_location  # Согласен, незачем лишние итерации
                break
        return new_map

    def select_way(self, win_exp):
        new_map = None
        print("""
        Выберите действие:
              1. Убить монстра
              2. Перейти в другую локацию
              3. Сдаться и выйти из игры
              """)
        choice = input()
        if choice == '1':
            self.kill_npc()
        elif choice == '2':
            new_map = self.select_new_location()
            if 'Hatch' in str(new_map.keys()):
                if self.current_experience < win_exp:
                    cprint('У вас ни опыта, ни мужества чтобы открыть этот люк с надписью "Exit"', 'red')
                    raise ValueError('После отчаяных попыток пробить люк, титановые руки вышли их строя...\n'
                                     'Быть может стоило просто повернуть ту ручку слева?'
                                     'Вот что значит отсутствие опыта((')

        elif choice == '3':
            raise GameQuitException
        else:
            raise ValueError('BANG! Кажется вы промахнулись в выборе и случайно расшибли лоб... помутнение...R.I.P')

        return new_map

    def run(self, rpg_map, remaining_timer, win_exp):
        new_map = rpg_map
        while True:
            if new_map:
                self.inspect_map(new_map)

            cprint(f'В находитесь в локации {self.current_location}', 'yellow')
            cprint(f'У вас {self.current_experience} ед. опыта и '
                   f'осталось {remaining_timer - self.game_timer} секунд', 'yellow')
            self.time_elapsed = datetime.datetime.now() - self.current_date
            cprint(f'Времени прошло: {str(self.time_elapsed).split(".")[0]}', 'yellow')

            if (remaining_timer - self.game_timer) < 0:
                raise GameOverException

            if self.current_location.startswith('Hatch'):
                raise GameOverException(''.join(self.current_npc))

            self.inspect_current_location()
            new_map = self.select_way(win_exp)


if __name__ == '__main__':

    remaining_time = '123456.0987654321'
    # если изначально не писать число в виде строки - теряется точность!
    field_names = ['current_location', 'current_experience', 'current_date']
    experience_for_win = 280

    json_map = 'rpg.json'
    csv_filepath = 'dungeon_stat.csv'

    with open(csv_filepath, 'w', newline='') as out_csv:
        writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=field_names, )
        writer.writeheader()

    game = Game(json_map, remaining_time, experience_for_win)

    while True:
        Jackson = Hero()
        try:
            Jackson.run(game.rpg_map, game.remaining_timer, game.experience_for_win)

        except ValueError as exc:
            cprint(f'{"".join(exc.args)}', 'red')
            print('Loading.')
            time.sleep(1)
            print('Loading..')
            time.sleep(1)
            print('Loading...\n')
            time.sleep(1)

            continue

        except IndexError as exc:
            cprint("".join(exc.args), 'red')
            continue

        except GameQuitException:
            cprint(game_over_fairy_tail(), 'yellow')
            print('\n -------- The End -------\n')
            exit()

        except GameOverException as exc:
            if exc.args:
                cprint(','.join(exc.args), 'blue')
                exit()
            else:
                cprint("""
                Вы не успели открыть люк!!! НАВОДНЕНИЕ!!! Алярм!
    
                У вас темнеет в глазах... прощай, титановый сплав...
                Но что это?! Вы воскресли у входа в пещеру... Не зря матушка дала комбинацию "[-> -> Y]" :)
                Ну, на этот-то раз у вас все получится! Трепещите, монстры!
                Вы неосторожно входите в пещеру... ;)
                """, 'yellow')
                continue

        finally:
            field_values = [Jackson.current_location,
                            Jackson.current_experience,
                            str(Jackson.time_elapsed).split(".")[0]
                            ]
            write_statistic(field_names, field_values, csv_filepath)
