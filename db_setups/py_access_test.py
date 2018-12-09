#import MySQLdb
#db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='mysql')

import mysql.connector

try:
	mydb = mysql.connector.connect(
		host="127.0.0.1",
		user="root",
		passwd="mysql",
		auth_plugin='mysql_native_password'
	)
	mycursor = mydb.cursor()
	mycursor.execute("CREATE DATABASE mydatabase")
except: ...

try:
	mydb = mysql.connector.connect(
		host="127.0.0.1",
		user="root",
		passwd="mysql",
		auth_plugin='mysql_native_password',
		database='mydatabase'
	)
	mycursor = mydb.cursor()
	try:
		mycursor.execute('DROP TABLE html')
	except:
		...
	mycursor.execute('''CREATE TABLE html (
		url VARCHAR(255), 
		score DOUBLE, 
		data DATE, 
		title BLOB, 
		body BLOB,
		UNIQUE KEY (url)
		)''')
except Exception as ex: 
	print(ex)
	...

