import sqlite3

def make_database():

    connect = sqlite3.connect("businesses.db")

    # connect.execute("DROP TABLE IF EXISTS BUSINESSES")

    # # SQL command to create a table
    # # executing pure sql code in python
    # connect.execute('''CREATE TABLE BUSINESSES
    #                 (ID INT PRIMARY KEY NOT NULL,
    #                 NAME TEXT NOT NULL,
    #                 TYPE TEXT NOT NULL,
    #                 LOCATION TEXT NOT NULL); 
    #                 ''')

    # create businesses table
    connect.execute('''
    CREATE TABLE IF NOT EXISTS BUSINESSES
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL);
    ''')

    # create products table
    connect.execute('''
    CREATE TABLE IF NOT EXISTS PRODUCTS
    (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PRODUCT_ID INTEGER NOT NULL,
    PRODUCT_NAME TEXT NOT NULL,
    PRODUCT_PRICE INTEGER NOT NULL,
    PRODUCT_DESCRIPTION TEXT NOT NULL,
    PRODUCT_TAGS TEXT,
    FOREIGN KEY (PRODUCT_ID) REFERENCES BUSINESSES(ID));
    ''')

    connect.close()
