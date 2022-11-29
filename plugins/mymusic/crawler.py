import requests
import json


# 全局用到变量
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

def search_song(song_name, return_limit=10):
    # 这是一个api接口
    # 参考自 https://www.showdoc.com.cn/ncj114514/9383824409721446
    search_url = f"http://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={song_name}&type=1&offset=0&total=true&limit={return_limit}"
    response = requests.get(url=search_url, headers=headers)
    # 如果成功，返回的应该是一个json列表
    json_dic = json.loads(response.text)
    songs = json_dic['result']['songs']
    print(f'总共搜索到{len(songs)}首歌曲!')
    return songs


def download_song(song_name, song_id):
    song_url = f"http://music.163.com/song/media/outer/url?id={song_id}"
    response = requests.get(song_url, headers = headers)
    content = response.content
    # 判断是否是MP3文件，有时候如果那首个没有版权是没有办法下载的
    if content[:3] != b'ID3':  # MP3文件以ID3开头
        print('不是MP3文件')
        return
    # 以二进制的方式写入 wb
    # with open(f'songs/{song_name}.mp3',mode='wb') as f:
    #     f.write(content)
    print(f'歌曲 {song_name} 下载成功！')
    return content
    
    
        
