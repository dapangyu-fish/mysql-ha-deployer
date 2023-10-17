import mysql.connector

db_master = mysql.connector.connect(
  host="172.88.88.3",
  user="root",
  password="password"
)

db_slave_1 = mysql.connector.connect(
  host="172.88.88.4",
  user="fish",
  password="password"
)

db_slave_2 = mysql.connector.connect(
  host="172.88.88.5",
  user="fish",
  password="password"
)

print(db_master)
print(db_slave_1)
print(db_slave_2)