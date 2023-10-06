import mysql.connector

def getConnection():
    return mysql.connector.connect(user='root', host='localhost', port=3306, database='watchlist')