import sqlite3

connect  = sqlite3.connect("/Users/user/Documents/Projects/technovation/database-sql/businesses.db")

# connect.execute("DROP TABLE IF EXISTS BUSINESSES")

# # SQL command to create a table
# # executing pure sql code in python
# connect.execute('''CREATE TABLE BUSINESSES
#                 (ID INT PRIMARY KEY NOT NULL,
#                 NAME TEXT NOT NULL,
#                 TYPE TEXT NOT NULL,
#                 LOCATION TEXT NOT NULL); 
#                 ''')

connect.execute("INSERT INTO BUSINESSES (ID, NAME, TYPE, LOCATION) VALUES (1, 'McDonalds', 'Fast Food', 'New York')")

all_data = connect.execute("""SELECT * FROM BUSINESSES""")
for row in all_data:
    print(row)

connect.close()
