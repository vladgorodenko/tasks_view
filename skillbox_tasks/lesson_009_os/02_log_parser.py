# -*- coding: utf-8 -*-

# Имеется файл events.txt вида:
#
# [2018-05-17 01:55:52.665804] NOK
# [2018-05-17 01:56:23.665804] OK
# [2018-05-17 01:56:55.665804] OK
# [2018-05-17 01:57:16.665804] NOK
# [2018-05-17 01:57:58.665804] OK
# ...
#
# Напишите программу, которая считывает файл
# и выводит число событий NOK за каждую минуту в другой файл в формате
#
# [2018-05-17 01:57] 1234
# [2018-05-17 01:58] 4321
# ...
#
# Входные параметры: файл для анализа, файл результата


class LogParser:

    def __init__(self, input_file_name=None):
        self.file_name = input_file_name
        self.event_list = []
        self.log = {}

    def collect_nok_events(self):
        if self.file_name is not None:
            with open(self.file_name, 'r', encoding='utf8') as input_file:
                for line in input_file:
                    if line.endswith('NOK\n'):
                        self.event_list.append(line)
        else:
            print('Не указан лог-файл событий')

    def collect_log(self):
        for event in self.event_list:
            if event in self.log:
                self.log[event] += 1
            else:
                self.log[event] = 1

    def get_group_by_value(self, value='minute'):
        if value is 'seconds':
            for i in range(len(self.event_list)):
                self.event_list[i] = self.event_list[i][:20] + ']'
        if value is 'minutes':
            for i in range(len(self.event_list)):
                self.event_list[i] = self.event_list[i][:17] + ']'
        elif value is 'hours':
            for i in range(len(self.event_list)):
                self.event_list[i] = self.event_list[i][:14] + ']'
        elif value is 'days':
            for i in range(len(self.event_list)):
                self.event_list[i] = self.event_list[i][:11] + ']'
        elif value is 'months':
            for i in range(len(self.event_list)):
                self.event_list[i] = self.event_list[i][:8] + ']'
        elif value is 'years':
            for i in range(len(self.event_list)):
                self.event_list[i] = self.event_list[i][:5] + ']'

    def unload_log(self, output_file_name=None):
        if output_file_name is not None:
            with open(output_file_name, 'w', encoding='utf8') as output_file:
                for time, event_count in self.log.items():
                    output_file.writelines(time + ' ' + str(event_count) + '\n')
        else:
            print('Не указан файл вывода лога')


parser = LogParser(input_file_name='events.txt')
parser.collect_nok_events()
parser.get_group_by_value(value='hours')
parser.collect_log()
parser.unload_log(output_file_name='out2.txt')


# зачет!



