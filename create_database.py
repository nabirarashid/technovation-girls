import sqlite3

def make_database():

    connect = sqlite3.connect("businesses.db")
    cursor = connect.cursor()

    # Create businesses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BUSINESSES
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL);
    ''')

    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PRODUCTS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    BUSINESS_ID INTEGER NOT NULL,
    PRODUCT_NAME TEXT NOT NULL,
    PRODUCT_PRICE INTEGER NOT NULL,
    PRODUCT_DESCRIPTION TEXT NOT NULL,
    PRODUCT_TAGS TEXT,
    PRODUCT_IMAGE BLOB NOT NULL,
    FOREIGN KEY (BUSINESS_ID) REFERENCES BUSINESSES(ID));
    ''')
    
    connect.commit()

    connect.close()
