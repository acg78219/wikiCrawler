# Python爬取维基百科的今日历史

## What

本项目利用 Python 爬取维基百科的每日历史页面的内容，并将数据保存到 Mysql 的 wikidb 数据库中，同时 saveJson.py 还能将 wikidb 数据库中的数据导出保存为 json 文件。



### 爬取的内容：

- 大事记
- 出生（包括图片）
- 逝世（包括图片）
- 维基首页“历史上的今天”中的五条历史事件（包括图片）



### 数据效果图：

![](https://raw.githubusercontent.com/acg78219/wikiCrawler/master/static/image/1.jpg)



![](https://raw.githubusercontent.com/acg78219/wikiCrawler/master/static/image/2.jpg)



### 文件

- spider.py
  - 爬取维基百科的内容，需要梯子。运行结果为各类型的数据保存到 Mysql 中的 wikidb 的表中。
- main.py
  - 读取 wikidb 各个表的内容，将数据导出至 json 文件。运行结果的文件保存在 json 文件夹下。
- json文件夹
  - 存放数据的 json 文件。
- images文件夹
  - 存放每一个历史事件的图片（如果有的话），并以日期划分文件夹。
- py文件夹
  - 存放从 wikidb 数据表中读取数据的 Python文件，供 saveJson.py 使用。



## How

1. 打开 spider.py ，执行前你需要在本地的 Mysql 中创建 wikidb 数据库，同时创建以下几个table：

### bigthing

| 键    | 数据类型 | 描述                        |
| ----- | -------- | --------------------------- |
| id    | int      | auto_increment、primary key |
| Thing | text     |                             |



### born

| 键    | 数据类型 | 描述                        |
| ----- | -------- | --------------------------- |
| id    | int      | auto_increment、primary key |
| Thing | text     |                             |



### death

| 键    | 数据类型 | 描述                        |
| ----- | -------- | --------------------------- |
| id    | int      | auto_increment、primary key |
| Thing | text     |                             |



### todayhistory

| 键    | 数据类型 | 描述                        |
| ----- | -------- | --------------------------- |
| id    | int      | auto_increment、primary key |
| year  | text     |                             |
| Thing | text     |                             |



2. 数据库初始化成功后，执行 spider.py，执行时间大概为 1min。执行成功后，爬取到的数据会保存在数据表中，图片会保存在 images 文件夹中。
3. 如果需要导出 Json 文件，打开 saveJson.py，直接执行。成功执行后，导出的文件会保存在json文件夹中。



*****

这个实战项目是本人的第一个项目，纯属兴趣使然，大家看看图一乐呵，也请各位 coder 多多指教！

code for tomorrow! 	;）
