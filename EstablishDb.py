from collections import deque
import urllib
import re
from bs4 import BeautifulSoup
import pymysql
import jieba
from DbOptimizer import func

config = {
          'host':'127.0.0.1',
          'port':3306,
          'user':'root',
          'password':'xxx',
          'database':'searchengine',
          'charset':'utf8mb4',
          'cursorclass':pymysql.cursors.Cursor}

#入口
#url = 'https://blog.csdn.net/chen_holy/article/details/90181282'
url = 'https://www.csdn.net/'

q = deque() #待爬取链接的双端队列，使用广度优先搜索
visited = set() #已访问的链接集合
q.append(url)

conn = pymysql.connect(**config)
c = conn.cursor()
c.execute('drop table doc')
c.execute('drop table word')
#在create table之前先drop table是因为我之前测试的时候已经建过table了，所以再次运行代码的时候得把旧的table删了重新建
c.execute('create table doc (id int primary key,link text)')
c.execute('create table word (term varchar(25) primary key,list text)')
conn.commit()
conn.close()

print('***************开始！***************************************************')
cnt = 0

# 当队列不为空时循环
# 最多抓取1000个url
while q and cnt <= 1000:
    url = q.popleft()
    visited.add(url)

    #爬取网页内容
    try:
        req = urllib.request.Request(url = url)
        res = urllib.request.urlopen(req)
        content = res.read().decode('utf-8')
    except:
        continue

    #寻找下一个可爬的链接，因为搜索范围是网站内，所以对链接有格式要求，这个格式要求根据具体情况而定
    m = re.findall(r'<a href="http.*?"', content, re.I)
    for x in m:
        x = x[9: -1]
        if (x not in visited) and (x not in q):
            q.append(x)

    #解析网页内容,可能有几种情况,这个也是根据这个网站网页的具体情况写的
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.title
    article = soup.find('h1')
    if article == None:
        article = soup.find('p')

    if title == None and article == None:
        print('无内容的页面')
        continue

    elif title != None and article == None:
        print('只有标题')
        title = title.get_text("", strip=True)
        article = ''

    elif title == None and article != None:
        print('只有内容')
        title = ''
        article = article.get_text("", strip=True)

    else:
        print('有标题有内容')
        title = title.get_text("", strip=True)
        article = article.get_text("", strip=True)

    cnt += 1
    print('开始抓取第', cnt, '个链接：', url)

    #提取出的网页内容存在title,article两个个字符串里，对它们进行中文分词
    seggen = jieba.cut_for_search(title)
    seglist = list(seggen)
    seggen = jieba.cut_for_search(article)
    seglist += list(seggen)

    #数据存储
    conn = pymysql.connect(**config)
    c = conn.cursor()
    c.execute('insert into doc values(%s,%s)', (cnt, url))

    #对每个分出的词语建立词表
    for word in seglist:
        #print(word)
        #检验看看这个词语是否已存在于数据库
        c.execute('select list from word where term=%s', word)
        result = c.fetchall()
        #如果不存在
        if len(result) == 0:
            docliststr = str(cnt)
            c.execute('insert into word values(%s,%s)', (word, docliststr))
        #如果已存在
        else:
            docliststr = result[0][0]#得到字符串
            docliststr += ' ' + str(cnt)
            c.execute('update word set list=%s where term=%s', (docliststr, word))

    conn.commit()
    conn.close()
print('词表建立完毕=======================================================')

func()

