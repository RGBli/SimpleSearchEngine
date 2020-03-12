import pymysql
import re

config = {
          'host':'127.0.0.1',
          'port':3306,
          'user':'root',
          'password':'xxx',
          'database':'searchengine',
          'charset':'utf8mb4',
          'cursorclass':pymysql.cursors.Cursor}

def func():
	print('开始优化数据库=======================================================')
	conn = pymysql.connect(**config)
	c = conn.cursor()
	# 计算原有元组个数
	c.execute('select count(*) from word')
	cnt_pre = c.fetchall()[0][0]

	c.execute('select term from word')
	res = c.fetchall()
	for i in res:
		s = i[0]
		isNum = True
		for ch in s:
			if (not ch.isdigit()):
				isNum = False

		if isNum or re.search(r'\w', s) == None:
			print("deleting " + s)
			c.execute('delete from word where term = %s', (s))

	c.execute('select count(*) from word')
	cnt_aft = c.fetchall()[0][0]
	conn.commit()
	conn.close()
	print('删去了', cnt_pre - cnt_aft, '个无效项')
	print('现有', cnt_aft, '个单词元组')
	print('数据库优化完毕=======================================================')