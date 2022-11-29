import os
import psutil
from pprint import pprint

print(psutil.cpu_count()) # 返回logic cpu 个数
print(psutil.cpu_percent(interval=2, percpu=True))
print(psutil.cpu_stats())
print(psutil.cpu_times())
#pprint(psutil.net_connections())
#pprint(psutil.pids())

p = psutil.Process(68816)
print(p.name())
print(p.exe())

for ps in psutil.process_iter():
    if ps.name().lower() == 'wechat.exe':
        print(ps.name(), ps.pid)