import sqlite3

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
'''
CREATE TABLE IF NOT EXISTS BUSINESSES
(ID INT PRIMARY KEY AUTOINCREMENT,
NAME TEXT NOT NULL);
'''

# create products table
'''
CREATE TABLE IF NOT EXISTS PRODUCTS
(
ID INT PRIMARY KEY AUTOINCREMENT,
BUSINESS(ID) INT NOT NULL,
PRODUCT_NAME TEXT NOT NULL,
PRODUCT_PRICE INT NOT NULL,
PRODUCT_DESCRIPTION TEXT NOT NULL,
PRODUCT_TAGS TEXT,
FOREIGN KEY (PRODUCT_ID) REFERENCES BUSINESSES(ID));
'''

#connect.execute("INSERT INTO BUSINESSES (ID, NAME, TYPE, LOCATION) VALUES (1, 'McDonalds', 'Fast Food', 'New York')")

# all_data = connect.execute("""SELECT * FROM BUSINESSES""")
# for row in all_data:
#     print(row)
# 
# connect.close()
