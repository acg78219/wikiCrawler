# -*- coding=utf-8 -*-
# @Time: 2021/6/21 19:57
# @Author: xlao
# @Software: PyCharm
import time

from bs4 import BeautifulSoup   # 解析网页数据
import requests     # requests 版本不能太高，不然会出错
import re
import xlwt
import sqlite3
import urllib.request   # 获取网页数据
import urllib.error
import datetime
import pymysql
import os

findUl = re.compile(r'<ul><li>([\s\S]*)</li></ul>')
findLi = re.compile(r'(li)')
findThing = re.compile(r'(li|h2)')   # 找到 li、h2、h3 标签
findDl = re.compile(r'(dt|dd)')    #找到所有 dt、dd
findDd = re.compile(r'(dd)')
findLink = re.compile(r'<a href="(.*?)"')
findImg = re.compile(r'^//upload.wikimedia.org/wikipedia/commons/thumb/.*?(jpg)$')
findPng = re.compile(r'//upload.wikimedia.org/wikipedia/commons/thumb/.*?(png)')
reg = re.compile(r'<[^>]*>')  # 正则搜索<tag>标签
reg2 = re.compile(r'\[(.*)]')  # 去除[]
reg3 = re.compile(r'/[0-9]+(px).*[^/](jpg|png)$')  # 去除掉指定像素的后缀
reg4 = re.compile(r'(/thumb)')  # 去除/thumb
reg5 = re.compile(r'(节|日|风|俗|法)')
reg6 = re.compile(r'：(.*)，')
reg7 = re.compile(r'[^\.]\w*$') # 匹配图片的后缀
head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
        "Referer": "https://zh.wikipedia.org/wiki/"}    # Referer 指从哪个网页跳转过来，有些反爬虫会看这个，否则下载的图片会损坏
baseDir = "F:\\library\\python library\\wikiHistory\\images\\"+str(datetime.date.today())   # 图片的文件夹
def main():

    start = time.time()
    cleanDB()   # 先清除前一天数据库中的数据
    baseUrl = "https://zh.wikipedia.org/zh-cn/"
    homeUrl = "https://zh.wikipedia.org/zh-cn/Wikipedia:%E9%A6%96%E9%A1%B5"  # 首页url
    todayurl = getUrl(baseUrl)      # 今日的 url，因为中文会转 utf-8，所以在 getUrl 中做一层处理
    dataList = getData(todayurl)    # 爬虫维基上今日页面的数据
    homeData = getHomeData(homeUrl)     # 爬取首页的”历史上的今天“内容，homeData 是一个列表，列表第一个元素是包含历史上的今天的列表，第二个元素是图片链接列表
    saveDB(dataList, homeData)    # 保存到数据库里面
    saveImg(homeData, bornAndDeath(dataList))
    end = time.time()
    print("总共运行时间%fs" % (end - start))


def cleanDB():
    con = pymysql.connect(host="localhost", port=3306, user="root", password="562713187", database="wikidb")
    cur = con.cursor()
    try:
        sql1 = "delete from bigthing;"
        sql2 = "delete from born;"
        sql3 = "delete from death;"
        sql4 = "delete from todayhistory;"
        sql5 = "alter table bigthing AUTO_INCREMENT = 0;"
        sql6 = "alter table born AUTO_INCREMENT = 0;"
        sql7 = "alter table death AUTO_INCREMENT = 0;"
        sql8 = "alter table todayhistory AUTO_INCREMENT = 0;"
        cur.execute(sql1)
        cur.execute(sql2)
        cur.execute(sql3)
        cur.execute(sql4)
        cur.execute(sql5)
        cur.execute(sql6)
        cur.execute(sql7)
        cur.execute(sql8)
        con.commit()
    except Exception as err:
        print(err)
    cur.close()
    con.close()

# 此函数将传进来的 url 进行解析，返回 url 的 html 文件
def askUrl(url):
    #封装请求
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        respon = urllib.request.urlopen(request)  #用urllib打开request中封装的请求，将结果返回给respon
        html = respon.read().decode("utf-8")      #解析respond，并写进html中
    except Exception as err:
        print(err)
    return html

# 此函数将 url 中的中文转为 utf-8
def getUrl(url):
    date = datetime.date.today()
    todayurl = ""
    #”月“和”日“要转移成utf-8
    todayurl = url+str(date.month)+"%E6%9C%88"+str(date.day)+"%E6%97%A5"
    return todayurl

# 此函数的对象是维基上的今天日期的页面， 爬取的内容是大事记、出生、逝世的内容，返回数据列表
def getData(url):
    html = askUrl(url)  # 接收 html 文件
    soup = BeautifulSoup(html, "html.parser")   # 先解析整个网页
    item = soup.findAll("div", class_="mw-parser-output")   # 我们想要的内容在这个 div 里面
    soup2 = BeautifulSoup(str(item), "html.parser")  # 再解析一次，因为 bs 返回是一个 tag，下面要使用到 tag 的 findAll
    # 将开头的div和多余的table删掉（因为里面有多余的ul）——后面想办法提成函数
    for tag in soup2.findAll("div", {"class": {"toc", "reflist"}}):     # 找到所有 div 中 class = toc、reflist 的内容
        tag.decompose()     # 将找到的 tag 从 soup2 中删掉
    soup2.renderContents()  # 重新渲染 soup2
    for tag in soup2.findAll("table"):  # 跟上一个操作一样，想办法提成函数
        tag.decompose()
    soup2.renderContents()

    ulList = []
    # 找到所有ul标签
    for ulItem in soup2.findAll(findThing):     # findThing = re.compile(r'(li|h2)')    找到所有 li、h2
        ulItem = str(ulItem)
        content = reg.sub("", ulItem).replace("\n", "").replace(" ", "")    # 剔除掉标签，保留内容
        content = reg2.sub("", content)     # 在 content 中删掉[]
        ulList.append(content)      # 将内容加入到列表中
    return ulList

def getHomeData(url):
    html = askUrl(url)
    soup = BeautifulSoup(html, "html.parser")
    dataList = []
    imgList = []
    column = soup.find("div", id="column-otd")
    soup2 = BeautifulSoup(str(column), "html.parser")
    # 获取历史事件内容
    for item in soup2.findAll(findDl):
        content = str(item)
        content = reg.sub("", content).replace("\n", "").replace(" ", "")
        content = reg2.sub("", content)
        dataList.append(content)
    for item in soup2.findAll(findDd):
        ddList = []     # 每一个 dd（每一个历史事件）中的图片链接放在一个数组
        for aTag in item.findAll('a'):  # 查找所有的 a 标签
            link = aTag.attrs['href']   # 获取 a 标签的 href
            linkRes = gotoLink(link)
            if linkRes is not None:     # 有时候页面中没有图片的话会返回 None
                ddList.append(linkRes)
        imgList.append(ddList)
    return [dataList, imgList]

# 此函数进入传进来的 url，并爬取图片
def gotoLink(url):
    # 每个 url 前面都有相同的前缀，用 requests 进入 url，返回 url 的 html
    secondHtml = requests.get('https://zh.wikipedia.org'+url, headers=head)
    # 解析返回的 html
    soup = BeautifulSoup(secondHtml.text, 'html.parser')
    img = soup.find('img', src=findImg)
    if img is None:
        # 如果该网页没有 jpg 的话，找到页面中的所有 png
        png = soup.findAll('img', src=findPng)
        # 遍历所有的 png， 找到所有 width 大于 200 的，页面中有很多小的图标 png
        for item in png:
            pngWidth = int(item.attrs['width'])
            if pngWidth >= 200:
                pngLink = 'https:'+item.attrs['src']
                pngLink = reg3.sub("", pngLink)
                pngLink = reg4.sub("", pngLink)
                return pngLink
    else:
        imgLink = 'https:'+img.attrs['src']     # 找到 img 的 src，并且拼接完整 url
        # 上面的 imgLink 是小像素的，我们需要修改 url 返回原图
        imgLink = reg3.sub("", imgLink)
        imgLink = reg4.sub("", imgLink)
        return imgLink

# 此函数将数据列表加入到 mysql 数据库中
def saveDB(dataList, homeData):
    resList = listIndex(dataList)
    bigthingEnd = resList[0]
    bornEnd = resList[1]
    deathEnd = resList[2]

    # 连接数据库
    con = pymysql.connect(host="localhost", port=3306, user="root", password="562713187", database="wikidb")
    # 创建游标
    cur = con.cursor()
    # 修改 “bigthing” 表
    for index in range(1, bigthingEnd):    #左闭右开
        try:
            sql1 = '''
            insert into `bigthing`
            (Thing)
            values
            (%s)'''     #动态绑定值？
            cur.execute(sql1, dataList[index])  # 这里的 dataList[index] 就是插进数据库的 values
            con.commit()
        except Exception as err:
            print("bingthing出错")
            print(err)
    #修改 “born” 表
    for index in range(bigthingEnd+1, bornEnd):
        try:
            sql2 = '''
             insert into `born`
             (Thing)
             values
             (%s)'''  # 动态绑定值？
            cur.execute(sql2, dataList[index])
            con.commit()
        except Exception as err:
            print("born出错")
            print(err)
    #修改 “death” 表
    for index in range(bornEnd+1, deathEnd):
        try:
            sql3 = '''
             insert into `death`
             (Thing)
             values
             (%s)'''  # 动态绑定值？
            cur.execute(sql3, dataList[index])
            con.commit()
        except Exception as err:
            print("death出错")
            print(err)
    for index in range(0, len(homeData[0]), 2):     # 因为 homeData 这个列表的年份和事件都是独立成一个元素，为了插在同一行，步长要调整为2
        try:
            sql4 = '''
            insert into `todayhistory`
            (year, Thing)
            values
            (%s, %s);'''
            cur.execute(sql4, (homeData[0][index], homeData[0][index + 1]))     # 第一个是年份，第二个是事件
            con.commit()
        except Exception as err:
            print(err)
    cur.close()
    con.close()

def saveImg(homeData, peopleData):
    # # 如果没有今天日期的文件夹，就创建一个
    if not os.path.exists(baseDir):
        os.mkdir(baseDir)
    #   index 主要用来给文件命名，避免命名重复冲突
    for iIndex, iItem in enumerate(homeData[1]):   # 遍历时每一个元素是一个事件的所有图片的列表集合
        thingDir = baseDir + '\\' + str(iIndex)     #今天日期下每一个事件也要独立一个文件夹
        if not os.path.exists(thingDir):
            os.mkdir(thingDir)
        for jIndex, jItem in enumerate(iItem):     # 每一个元素是事件中的元素，图片链接
            suffix = '.' + reg7.search(jItem).group(0)
            try:
                pic = requests.get(jItem, headers=head, timeout=15)   # 利用 requests.get 方法获取图片 设置超时时间为 15 秒
            except requests.exceptions.ConnectionError:
                print('图片下载失败')
                continue
            fileName = thingDir + '\\' + str(jIndex) + suffix
            f = open(fileName, 'wb')    # wb 是以二进制的方式写入
            f.write(pic.content)        # 将 pic.content 写入
            f.close()
    for bornIndex, bornItem in enumerate(peopleData[0]):    # 这个 for 循环保存出生的人的图片
        bornDir = baseDir + '\\bornImg'
        if not os.path.exists(bornDir):
            os.mkdir(bornDir)
        if bornItem is not None:
            suffix = '.' + reg7.search(bornItem).group(0)   # 获得后缀
            try:
                pic = requests.get(bornItem, headers=head, timeout=15)
            except requests.exceptions.ConnectionError:
                print('图片下载失败')
                continue
            fileName = bornDir + '\\' + str(bornIndex) + suffix  # 加 1 是因为事件的 id 是从 1 开始的
            f = open(fileName, 'wb')  # wb 是以二进制的方式写入
            f.write(pic.content)  # 将 pic.content 写入
            f.close()
    for deathIndex, deathItem in enumerate(peopleData[1]):    # 这个 for 循环保存出生的人的图片
        deathDir = baseDir + '\\deathImg'
        if not os.path.exists(deathDir):
            os.mkdir(deathDir)
        if deathItem is not None:
            suffix = '.' + reg7.search(deathItem).group(0)   # 获得后缀
            try:
                pic = requests.get(deathItem, headers=head, timeout=15)
            except requests.exceptions.ConnectionError:
                print('图片下载失败')
                continue
            fileName = deathDir + '\\' + str(deathIndex) + suffix  # 加 1 是因为事件的 id 是从 1 开始的
            f = open(fileName, 'wb')  # wb 是以二进制的方式写入
            f.write(pic.content)  # 将 pic.content 写入
            f.close()


# 该函数查找爬取到的数据列表中，大事件、出生、逝世的下标，进行进一步列表分类
def listIndex(dataList):
    bigthingEnd = 0
    bornEnd = 0
    deathEnd = 0
    for index, data in enumerate(dataList):  # data代表数据中的一个元素
        if data == "出生":
            bigthingEnd = index
        if data == "逝世":
            bornEnd = index
        if re.match(reg5, data):  # 维基里面 “节假日和风俗” 这一字符串有时候不一定是这个，可能是 “节日” 之类的，所以用正则判断一下
            deathEnd = index
    return [bigthingEnd, bornEnd, deathEnd]

# 该函数查找出生和逝世的名人的图片链接
def bornAndDeath(dataList):
    # 出生和逝世分开的原因是后面需要根据图片的命名来判断哪个内容放哪张图片
    bornData = []   # 这个存放出生的数据
    deathData = []  # 这个存放逝世的数据
    # 获取事件类型的下标，确定边界
    resList = listIndex(dataList)
    bigthingEnd = resList[0]
    bornEnd = resList[1]
    deathEnd = resList[2]
    # 搜索出生的人的图片
    for index in range(bigthingEnd+1, bornEnd):
        people = reg6.search(dataList[index])
        # 如果没有截取到这个人的话就返回 None
        if people is not None:
            people = people.group(0).replace("：", "").replace("，", "")
            bornData.append(gotoPeople(people))
        else:
            bornData.append(people)
    #  这是搜索逝世的人的图片
    for index in range(bornEnd+1, deathEnd):
        people = reg6.search(dataList[index])
        # 如果没有截取到这个人的话就返回 None
        if people is not None:
            people = people.group(0).replace("：", "").replace("，", "")
            deathData.append(gotoPeople(people))
        else:
            deathData.append(people)
    return [bornData, deathData]

def gotoPeople(url):
    secondHtml = requests.get('https://zh.wikipedia.org/wiki/' + url, headers=head)
    soup = BeautifulSoup(secondHtml.text, 'html.parser')
    img = soup.find('img', src=findImg)
    # 如果这个网页没有图片就返回 None
    if img is not None:
        imgLink = 'https:'+img.attrs['src']
        imgLink = reg3.sub("", imgLink)
        imgLink = reg4.sub("", imgLink)
        return imgLink
    else:
        return img


if __name__ == "__main__":
    main()