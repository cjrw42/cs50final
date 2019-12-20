#!/usr/bin/python3

import sqlite3

conn=sqlite3.connect('sensorlog')
print("opened database")

conn.execute('CREATE TABLE Employees (ID INT PRIMARY KEY NOT NULL, NAME TEXT NOT NULL, AGE INT NOT NULL, ADDRESS CHAR(50),SALARY REAL);')  
print ("Table created successfully")  
  
conn.close()  


print("done")
