import sys
import requests
from bs4 import BeautifulSoup
import requests
import re


def get_response(location='guangzhou'):
    headers = { 'User-Agent' : 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36' }
    response = requests.get('https://www.tianqi.com/{0}/'.format(location), headers=headers)
    return response

def parse_response(response):
    weather_info = {}
    soup = BeautifulSoup(response.text, 'html.parser')
    # 中间处理阶段
    loc_node = soup.select('dd.name')[0]
    weather_node = soup.select('p.now')[0]
    cloud_node = weather_node.find_next_sibling("span")
    air_node = soup.select('dd.kongqi')[0]
    shidu_node = soup.select('dd.shidu')[0]
    week_node = soup.select('dd.week')[0]
    sun = list(air_node.children)[2]
    # 提取最终信息到字典里
    weather_info['name'] = list(loc_node.children)[0].text
    weather_info['temperature'] = weather_node.text
    weather_info['cloud'] = list(cloud_node.children)[0].text
    weather_info['temp_range'] = list(cloud_node.children)[1]
    weather_info['air_condition'] = list(air_node.children)[0].text.split('：')[-1]
    weather_info['PM'] = list(air_node.children)[1].text.split(' ')[-1]
    weather_info['sunrise'] = list(sun.children)[0].split(': ')[-1]  # NavigableString
    weather_info['sunset'] = list(sun.children)[2].split(': ')[-1]   # NavagableString
    weather_info['humidity'] = list(shidu_node.children)[0].text.split('：')[-1]  # <b>tag
    weather_info['wind_direction'] = list(shidu_node.children)[1].text.split('：')[-1] # <b>tag
    weather_info['ultraviolet'] = list(shidu_node.children)[2].text.split('：')[-1] # <b>tag
    # 原本是这样的字符串 '2022年10月22日\u3000星期六\u3000壬寅年九月廿七 霜降'，包含了\u3000 和 空格
    weather_info['date'], weather_info['week'], weather_info['lunar_date'], weather_info['solar_term'] = \
        re.split('[\u3000|\s]', week_node.text)
        
    return weather_info

def get_weather_by_loc(location='guanzhou'):
    response = get_response(location)
    weather = parse_response(response)
    return weather

def print_weather(weather):
    print('标题：' + weather['name'])
    print('日出：' + weather['sunrise'])
    print('日落：' + weather['sunset'])
    print('气温：' + weather['temperature'])
    print('云：' + weather['cloud'])
    print('气温范围：' + weather['temp_range'])
    print('空气质量：' + weather['air_condition'])
    print('PM指数：' + weather['PM'])
    print('湿度：' + weather['humidity'])
    print('风向：' + weather['wind_direction'])
    print('紫外线：' + weather['ultraviolet'])
    print('日期：' + weather['date'])
    print('星期：' + weather['week'])
    print('农历日期：' + weather['lunar_date'])
    print('节气：' + weather['solar_term'])


#response.encoding='utf-8'





print(sys.argv[0])
print(sys.argv)
weather = get_weather_by_loc(sys.argv[1])
print(weather)
print_weather(weather)