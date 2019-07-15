#:@TIME    : 2019/7/11 9:52
#:@Author  : qiheirumo
#:@File    : manhuazhijia.PY

import random
import urllib

import os


import time
import execjs
import json

import requests
from bs4 import BeautifulSoup

from JXMysqlUtil import PymysqlUtil

URL = "https://www.dmzj.com/info/yaosushan.html"

IMG_URL_PREX = "https://images.dmzj.com/"

FileFolder = "D:\\Python漫画\\妖宿山"


header = [{
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'},
        {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
        {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
        {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
        {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'}]

mysql = PymysqlUtil("localhost", 3306, "root", "xxxxx", "python", "utf8")

proxy=[]

CHAPTER_LIST=[];


#建立ip代理信息
def get_proxy():
    # 获取ip池
    list = mysql.get_all("select ip,port,id from ip_pool")
    for item in list:
        proxy.append({"http":"http://" + item[0] + ":" + item[1]})


#主函数
def main():
    #先准备好ip连接池
    get_proxy()
    # 准备爬取章节链接
    flag = True
    while(flag):
        flag = start(doPost(URL));
        print(flag);
    # 准备爬取每一章的数据
    getContent();


def getContent():
    for item in CHAPTER_LIST:
        print(item.get("title"))
        print(item.get("url"))
        soup = doPost(item.get("url"))
        strEVAL= soup.find("script").get_text()
        lll = strEVAL.split(";",2)
        parse_str = lll[2];
        parse_str = parse_str.replace("\n","")
        parse_str = parse_str.replace('function(p,a,c,k,e,d)', 'function fun(p, a, c, k, e, d)')
        parse_str = parse_str.replace('eval(', '').strip(" ")[:-1]  # 去除eval
        fun = r"""
                        function run(){
                            var pages = %s;
                            pages = pages.replace(/\n/g,"");
                            pages = pages.replace(/\r/g,"|");
                            return pages;
                        }
                    """ % parse_str  # 构造函数调用产生pages变量结果
        pages = execjs.compile(fun).call('run')
        xxx = pages.split("'", 2)
        page =xxx[1];
        page = json.loads(page);
        img = page.get("page_url");
        img_list = img.split("\r\n")
        num = 0;
        CHAP = item.get("title").replace(" ","")
        for p in img_list:
            PATH = FileFolder+"\\"+CHAP+"\\";
            isExists = os.path.exists(PATH)
            if not isExists:
                os.makedirs(PATH)
            flag = True
            while(flag):
                try:
                    f = open(PATH + str(num) + '.jpg', 'wb')
                    f.write((urllib.request.urlopen(IMG_URL_PREX + urllib.parse.quote(p), timeout=3)).read())
                    f.close()
                    flag = False
                except:
                    f.close()
                    print("下载失败！第"+str(num)+"张图片正重新发起下载")
            num += 1
            print("第" + str(num) + "张完成")








#开始获取所有章节
def start(soup):
    zj_list = soup.find("div",class_="tab-content tab-content-selected zj_list_con autoHeight")
    if zj_list is not None:
        urlList = zj_list.find_all("a")
        for item in urlList:
            dic ={};
            dic["title"] = item.attrs["title"]
            dic["url"] = item.attrs["href"]
            CHAPTER_LIST.append(dic)
        return False
    else:
        print("获取数据异常")
        return True

def doPost(url):
    count = 0;
    while (True):
        req = None;
        try:
            req = requests.get(url, headers=header[random.randint(0, 4)],
                               proxies=proxy[random.randint(0, len(proxy) - 1)], timeout=3)
        except:
            count += 1
            print("连接超时,3秒后", "尝试第", count, "次重连！")
            time.sleep(3)

        if req is not None:
            break
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, "html.parser")
    return soup



if __name__ == '__main__':
    main()
    #getContent()

    # s = "   abc    ";
    # print(s.replace("a","c").strip(" ")[:-1])
