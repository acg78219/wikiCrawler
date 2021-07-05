# Python爬取维基百科的今日历史

## What

本项目利用 Python 爬取维基百科的每日历史页面的内容，并将数据保存到 Mysql 的 wikidb 数据库中，同时 saveJson.py 还能将 wikidb 数据库中的数据导出保存为 json 文件。



### 爬取的内容：

- 大事记
- 出生（包括图片）
- 逝世（包括图片）
- 维基首页“历史上的今天”中的五条历史事件（包括图片）



### 文件

- spider.py
  - 爬取维基百科的内容，需要梯子。运行结果为各类型的数据保存到 Mysql 中的 wikidb 的表中。
- main.py
  - 读取 wikidb 各个表的内容，将数据导出至 json 文件。运行结果的文件保存在 json 文件夹下。
- json文件夹
  - 存放数据的 json 文件
- images文件夹
  - 存放每一个历史事件的图片（如果有的话），并以日期划分文件夹
- 
