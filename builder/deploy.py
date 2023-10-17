import mysql.connector

db_master = mysql.connector.connect(
  host="172.88.88.3",
  user="stnduser",
  password="stnduser"
)

db_slave_1 = mysql.connector.connect(
  host="172.88.88.4",
  user="stnduser",
  password="stnduser"
)

db_slave_2 = mysql.connector.connect(
  host="172.88.88.5",
  user="stnduser",
  password="stnduser"
)

print(db_master)
print(db_slave_1)
print(db_slave_2)