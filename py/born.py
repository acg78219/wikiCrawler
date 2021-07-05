import pymysql
import json

def bornToJson():
    try:
        #连接数据库
        con = pymysql.connect(host='localhost', user='root',password='562713187',db='wikidb', port=3306, charset='utf8')
        #创建游标
        cur = con.cursor()
        sql = "select * from born"
        #执行sql语句
        cur.execute(sql)
        #execute执行后的数据放在缓存区，用fetchall接收全部给data，data是元组(不可修改的数组)
        data = cur.fetchall()
        cur.close()
        con.close()
        jsonData = []   #数据中一个元素就是一行记录
        for row in data:
            result = {"id": row[0], "Thing": row[1]}  #每个元素是一个对象
            jsonData.append(result)
        return jsonData
    except Exception as err:
        print(err)

#每一个字段之间加回车换行
def modJson(jsonData):
    jsonDataStr = '\n'.join(map(str, jsonData))
    return jsonDataStr

def go():
    jsonData = modJson(bornToJson())
    f = open(r'json/born.json', 'w+', encoding='utf-8')   #w+:读写
    f.write(jsonData)
    f.close()
