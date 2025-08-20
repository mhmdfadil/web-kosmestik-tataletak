from flask_mysqldb import MySQL
from flask import g

mysql = MySQL()

def get_db():
    if 'mysql_db' not in g:
        g.mysql_db = mysql.connection
    return g.mysql_db
