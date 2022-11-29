from plugins.weather import weather
from plugins.mymusic import  crawler
print(weather.get_weather_by_loc('guangzhou'))
print(crawler.search_song('东方'))