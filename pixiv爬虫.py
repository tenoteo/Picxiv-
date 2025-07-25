from bs4 import BeautifulSoup
import json
import requests
import re
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import random

def getName(img_id,headers):
    try:
        urll=f"https://www.pixiv.net/artworks/{img_id}"
        
        rep=session.get(urll,headers=headers)
        rep.raise_for_status()
        
        obj1=rep.text
        text_data=BeautifulSoup(obj1,"html.parser")
        artist_text=text_data.find("meta", property="og:title")
        if artist_text is None:
            raise ValueError('未取得标签')
        obj2=re.compile(r'<meta content=".*?- (?P<artist>.*?)的插画',re.S)
        artist_names=obj2.findall(str(artist_text))
             
        if artist_names is None:
             raise ValueError('未找到艺术家名称')
        artist_name=artist_names[0]
        illegal_chars = r'[\\/:*?"<>|\x00-\x1F]'
        artist_name= re.sub(illegal_chars, '_', artist_name)
        return artist_name
    except requests.exceptions.RequestException as e:
         print(f"请求错误:{e}")
         return None
    except ValueError as e:
         print(f"解析错误:{e}")
         return None
    except IndexError:
         print("未找到艺术家名称")
         return None


def Down_by_Artwork_id(img_id,headers,session):
    try:
        second=random.randint(1,4)
        url=f'https://www.pixiv.net/ajax/illust/{img_id}/pages?lang=zh'
        trps=session.get(url,headers=headers)
        trps.raise_for_status()
        page=trps.json()['body']
        artist_name=getName(img_id,headers)
        if artist_name is None:
                artist_name="Unkown"
        for imgs in page:
            img_src=imgs['urls']['original']
            img=session.get(img_src,headers=headers)
            img_name=img_src.split('/')[-1]
            download_dir = Path(artist_name)
            download_dir.mkdir(exist_ok=True)
            save_path= download_dir / f"{artist_name} {img_name}"
            with open(save_path,mode='wb') as f:
                    f.write(img.content)
            f.close()
            print(f"{img_id} 下载完毕!")
            time.sleep(second)
            trps.close()

    except json.decoder.JSONDecodeError:
        print("Cookie 过期")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except KeyError as e:
        print(f"数据结构错误，未找到键: {e}")
    except Exception as e:
        print(f"下载过程中发生未知错误: {e}")

def down_all_artist_from_artsist(id,headers,session):
        user_id=f"https://www.pixiv.net/ajax/user/{id}/profile/all?lang=zh"
        
        
        rspd=session.get(user_id,headers=headers)
        rspd.raise_for_status()
        art_lists_original=rspd.json()['body']['illusts']
        artist=rspd.json()['body']['pickup'][0]['userName']
        print(artist)
        #art_lists=re.findall(r"'(?P<art_list>.*?)'",str(art_lists_original))
        art_lists=list(art_lists_original.keys())
        if art_lists is None:
             raise ValueError('列表为空')
        print('所有作品Id如下: ')
        print(art_lists)
        print(f"大概下载图片数: {len(art_lists)}+")
        start_time=time.time()
        print("开始下载...")
        with ThreadPoolExecutor(max_workers=5) as t:
            objs=[]
            for id in art_lists:
                 obj=t.submit(Down_by_Artwork_id,id,headers,session)
                 objs.append(obj)
                 print(f"{id}正在下载")

            for obj in objs:
                 obj.result()
            tot_time=time.time()-start_time
            print(f"共用时 {tot_time:.2f} 秒")
def switch(a):
    match a:
        case '1':
               id_num=input("请输入作品id: ")
               id=int(id_num)
               Down_by_Artwork_id(id,headers,session)
               a=input("请输入数字: ")
        case '2':
                id_num=input("请输入作者id: ")
                id=int(id_num)
                down_all_artist_from_artsist(id,headers,session)
                a=input("请输入数字: ")
        case '3':
              return 0
if __name__ == "__main__":
    try:
        #img_id=input("输入pid: ")
        
        #img_id=int(img_id)
        session=requests.session()
        headers={
            'referer':'https://www.pixiv.net/',
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "cookie":"#"
        }
        print("-----------\n","1.以作品id下载\n","2.以作者id下载全部\n","3.退出","-----------\n")
        while True:
            n=input("请输入数字: ")
            if n is None:
                raise ValueError("请输入数字!")
            if n=="1":
                id_num=input("请输入作品id: ")
                id=int(id_num)
                Down_by_Artwork_id(id,headers,session)
                continue
            if n=="2":
                id_num=input("请输入作者id: ")
                id=int(id_num)
                down_all_artist_from_artsist(id,headers,session)
                continue
            if n=="3":
                 break
            

        
    except ValueError:
         print('输入的pid有问题')
    except Exception as e:
         print("程序启动有误")
