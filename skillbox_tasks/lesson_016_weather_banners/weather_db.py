import peewee

database_proxy = peewee.DatabaseProxy()


class BaseTable(peewee.Model):
    # В подклассе Meta указываем подключение к той или иной базе данных
    class Meta:
        database = database_proxy


class Cities(BaseTable):
    city_en = peewee.CharField()
    city_ru = peewee.CharField()
    city_ru_pp = peewee.CharField()


class WeatherJournal(BaseTable):
    source = peewee.CharField()
    city = peewee.ForeignKeyField(Cities.city_en)
    t_day = peewee.IntegerField()
    t_night = peewee.IntegerField()
    date = peewee.DateField('%y-%m-%d')
    weather_status = peewee.CharField()



