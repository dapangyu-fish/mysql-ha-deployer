import mysql.connector

db_proxy= mysql.connector.connect(
  host="172.88.88.2",
  user="admin",
  password="admin"
)

db_master = mysql.connector.connect(
  host="172.88.88.3",
  user="root",
  password="password"
)

db_slave_1 = mysql.connector.connect(
  host="172.88.88.4",
  user="root",
  password="password"
)

db_slave_2 = mysql.connector.connect(
  host="172.88.88.5",
  user="root",
  password="password"
)

print(db_master)
print(db_slave_1)
print(db_slave_2)