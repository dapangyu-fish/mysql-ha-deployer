# mysql-ha-deployer
- create bridge
```create bridge
docker network create --subnet=172.88.88.0/24 ha-mysql
```
- clean all
```clean all

docker rm -f proxysql
docker rm -f mysql1
docker rm -f mysql2
docker rm -f mysql3
docker rm -f mysql4
docker rm -f mysql5
docker run --hostname mysql1 --net ha-mysql --ip 172.88.88.103 --restart=always --name mysql1 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 --add-host=mysql4:172.88.88.106 --add-host=mysql5:172.88.88.107 mysql:latest
docker run --hostname mysql2 --net ha-mysql --ip 172.88.88.104 --restart=always --name mysql2 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 --add-host=mysql4:172.88.88.106 --add-host=mysql5:172.88.88.107 mysql:latest
docker run --hostname mysql3 --net ha-mysql --ip 172.88.88.105 --restart=always --name mysql3 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 --add-host=mysql4:172.88.88.106 --add-host=mysql5:172.88.88.107 mysql:latest
docker run --hostname mysql4 --net ha-mysql --ip 172.88.88.106 --restart=always --name mysql4 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 --add-host=mysql4:172.88.88.106 --add-host=mysql5:172.88.88.107 mysql:latest
docker run --hostname mysql5 --net ha-mysql --ip 172.88.88.107 --restart=always --name mysql5 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 --add-host=mysql4:172.88.88.106 --add-host=mysql5:172.88.88.107 mysql:latest

```


# https://blog.51cto.com/u_15080860/6075927

- mysql1
```
docker exec -it mysql1 bash

mysql -u root -ppassword

SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';
install PLUGIN group_replication SONAME 'group_replication.so';
SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';

exit

cat <<EOF >> /etc/my.cnf
[mysqld]
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
server_id=1 #其它节点相应修改，不能重复
gtid_mode=ON
enforce_gtid_consistency=ON
binlog_checksum=NONE
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
transaction_write_set_extraction=XXHASH64
plugin_load_add='group_replication.so'
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.103:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061"
group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107"
group_replication_bootstrap_group=off
max_connections=500
EOF

# 重启mysql

docker exec -it mysql1 bash

mysql -u root -ppassword

SET SQL_LOG_BIN=0;
create user rpl_user@'%' identified with mysql_native_password by 'Rpl_user123';
GRANT REPLICATION SLAVE ON *.* TO rpl_user@'%';
GRANT BACKUP_ADMIN ON *.* TO rpl_user@'%';
FLUSH PRIVILEGES;
SET SQL_LOG_BIN=1;


SET GLOBAL group_replication_bootstrap_group=ON;

set global group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105";
CHANGE MASTER TO MASTER_USER='rpl_user', MASTER_PASSWORD='Rpl_user123' FOR CHANNEL 'group_replication_recovery';


start group_replication;


SELECT * FROM performance_schema.replication_group_members;


SET GLOBAL group_replication_bootstrap_group=OFF;


exit
exit
```

- mysql2
```
docker exec -it mysql2 bash


mysql -u root -ppassword

SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';
install PLUGIN group_replication SONAME 'group_replication.so';
SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';

exit


cat <<EOF >> /etc/my.cnf
[mysqld]
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
server_id=2 #其它节点相应修改，不能重复
gtid_mode=ON
enforce_gtid_consistency=ON
binlog_checksum=NONE
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
transaction_write_set_extraction=XXHASH64
plugin_load_add='group_replication.so'
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.104:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061,172.88.88.106:33061,172.88.88.107:33061"
group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107"
group_replication_bootstrap_group=off
max_connections=500
EOF

# 重启mysql

docker exec -it mysql2 bash


mysql -u root -ppassword


SET SQL_LOG_BIN=0;
create user rpl_user@'%' identified with mysql_native_password by 'Rpl_user123';
GRANT REPLICATION SLAVE ON *.* TO rpl_user@'%';
GRANT BACKUP_ADMIN ON *.* TO rpl_user@'%';
FLUSH PRIVILEGES;
SET SQL_LOG_BIN=1;

set global group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105";
CHANGE MASTER TO MASTER_USER='rpl_user', MASTER_PASSWORD='Rpl_user123' FOR CHANNEL 'group_replication_recovery';

START GROUP_REPLICATION;

SELECT * FROM performance_schema.replication_group_members;


```

- mysql3
```
docker exec -it mysql3 bash


mysql -u root -ppassword

SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';
install PLUGIN group_replication SONAME 'group_replication.so';
SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';

exit


cat <<EOF >> /etc/my.cnf
[mysqld]
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
server_id=3 #其它节点相应修改，不能重复
gtid_mode=ON
enforce_gtid_consistency=ON
binlog_checksum=NONE
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
transaction_write_set_extraction=XXHASH64
plugin_load_add='group_replication.so'
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.105:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061,172.88.88.106:33061,172.88.88.107:33061"
group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107"
group_replication_bootstrap_group=off
max_connections=500
EOF

# 重启mysql

docker exec -it mysql3 bash


mysql -u root -ppassword


SET SQL_LOG_BIN=0;
create user rpl_user@'%' identified with mysql_native_password by 'Rpl_user123';
GRANT REPLICATION SLAVE ON *.* TO rpl_user@'%';
GRANT BACKUP_ADMIN ON *.* TO rpl_user@'%';
FLUSH PRIVILEGES;
SET SQL_LOG_BIN=1;

set global group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107";
CHANGE MASTER TO MASTER_USER='rpl_user', MASTER_PASSWORD='Rpl_user123' FOR CHANNEL 'group_replication_recovery';

START GROUP_REPLICATION;

SELECT * FROM performance_schema.replication_group_members;


```


- mysql4
```
docker exec -it mysql4 bash


mysql -u root -ppassword

SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';
install PLUGIN group_replication SONAME 'group_replication.so';
SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';

exit


cat <<EOF >> /etc/my.cnf
[mysqld]
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
server_id=4 #其它节点相应修改，不能重复
gtid_mode=ON
enforce_gtid_consistency=ON
binlog_checksum=NONE
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
transaction_write_set_extraction=XXHASH64
plugin_load_add='group_replication.so'
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.106:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061,172.88.88.106:33061,172.88.88.107:33061"
group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107"
group_replication_bootstrap_group=off
max_connections=500
EOF

# 重启mysql

docker exec -it mysql4 bash


mysql -u root -ppassword


SET SQL_LOG_BIN=0;
create user rpl_user@'%' identified with mysql_native_password by 'Rpl_user123';
GRANT REPLICATION SLAVE ON *.* TO rpl_user@'%';
GRANT BACKUP_ADMIN ON *.* TO rpl_user@'%';
FLUSH PRIVILEGES;
SET SQL_LOG_BIN=1;

set global group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107";
CHANGE MASTER TO MASTER_USER='rpl_user', MASTER_PASSWORD='Rpl_user123' FOR CHANNEL 'group_replication_recovery';

START GROUP_REPLICATION;

SELECT * FROM performance_schema.replication_group_members;


```

- mysql5
```
docker exec -it mysql5 bash


mysql -u root -ppassword

SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';
install PLUGIN group_replication SONAME 'group_replication.so';
SELECT   PLUGIN_NAME, PLUGIN_STATUS, PLUGIN_TYPE,   PLUGIN_LIBRARY, PLUGIN_LICENSE FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME LIKE 'group%' AND PLUGIN_STATUS='ACTIVE';

exit


cat <<EOF >> /etc/my.cnf
[mysqld]
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
server_id=5 #其它节点相应修改，不能重复
gtid_mode=ON
enforce_gtid_consistency=ON
binlog_checksum=NONE
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
transaction_write_set_extraction=XXHASH64
plugin_load_add='group_replication.so'
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.107:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061,172.88.88.106:33061,172.88.88.107:33061"
group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107"
group_replication_bootstrap_group=off
max_connections=500
EOF

# 重启mysql

docker exec -it mysql5 bash


mysql -u root -ppassword


SET SQL_LOG_BIN=0;
create user rpl_user@'%' identified with mysql_native_password by 'Rpl_user123';
GRANT REPLICATION SLAVE ON *.* TO rpl_user@'%';
GRANT BACKUP_ADMIN ON *.* TO rpl_user@'%';
FLUSH PRIVILEGES;
SET SQL_LOG_BIN=1;

set global group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105,172.88.88.106,172.88.88.107";
CHANGE MASTER TO MASTER_USER='rpl_user', MASTER_PASSWORD='Rpl_user123' FOR CHANNEL 'group_replication_recovery';

START GROUP_REPLICATION;

SELECT * FROM performance_schema.replication_group_members;


```

- test
```test
CREATE DATABASE fish1;
use fish1;
CREATE TABLE user ( username VARCHAR(255), age INT, id INT AUTO_INCREMENT PRIMARY KEY);
INSERT INTO user (username, age) VALUES ('fish-1', 25);
INSERT INTO user (username, age) VALUES ('fish-2', 30);
INSERT INTO user (username, age) VALUES ('fish-2', 35);

select * from user;

DROP TABLE user;
DROP DATABASE fish1;

docker exec -it mysql1 bash -c "sed -i 's/group_replication_start_on_boot=off/group_replication_start_on_boot=on/' /etc/my.cnf"
docker exec -it mysql2 bash -c "sed -i 's/group_replication_start_on_boot=off/group_replication_start_on_boot=on/' /etc/my.cnf"
docker exec -it mysql3 bash -c "sed -i 's/group_replication_start_on_boot=off/group_replication_start_on_boot=on/' /etc/my.cnf"
docker exec -it mysql4 bash -c "sed -i 's/group_replication_start_on_boot=off/group_replication_start_on_boot=on/' /etc/my.cnf"
docker exec -it mysql5 bash -c "sed -i 's/group_replication_start_on_boot=off/group_replication_start_on_boot=on/' /etc/my.cnf"
docker restart mysql5
docker restart mysql4
docker restart mysql3
docker restart mysql2
docker restart mysql1
```
    
# 单主切换到多主
```
SELECT group_replication_switch_to_multi_primary_mode()
```

# 多主切换到单主
```
SELECT group_replication_switch_to_single_primary_mode(‘7edd8b92-b077-11eb-8ffe-000c2936760d’);
```

```angular2html
docker run --net ha-mysql --ip 172.88.88.100 -p 16032:6032 -p 16033:6033 -p 16070:6070 -d --restart=always --name=proxysql proxysql/proxysql

docker exec -it proxysql bash

mysql -u admin -padmin -h 127.0.0.1 -P6032 --default-auth=mysql_native_password --prompt 'ProxySQL Admin> '

SELECT * FROM mysql_servers;
SELECT * from mysql_replication_hostgroups;
SELECT * from mysql_query_rules;

INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.103',3306);
INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.104',3306);
INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.105',3306);
INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.106',3306);
INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.107',3306);

SELECT * FROM mysql_servers;
LOAD MYSQL VARIABLES TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;
SELECT * FROM mysql_servers;

# 真实数据库操作

CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';

CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'fish'@'%';

docker exec -it proxysql bash
mysql -u admin -padmin -h 127.0.0.1 -P6032 --default-auth=mysql_native_password --prompt 'ProxySQL Admin> '
UPDATE global_variables SET variable_value='monitor' WHERE variable_name='mysql-monitor_username';
UPDATE global_variables SET variable_value='monitor' WHERE variable_name='mysql-monitor_password';
UPDATE global_variables SET variable_value='2000' WHERE variable_name IN ('mysql-monitor_connect_interval','mysql-monitor_ping_interval','mysql-monitor_read_only_interval');
SELECT * FROM global_variables WHERE variable_name LIKE 'mysql-monitor_%';


LOAD MYSQL USERS TO RUNTIME;
SAVE MYSQL USERS TO DISK;
LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL QUERY RULES TO DISK;
LOAD MYSQL VARIABLES TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;
LOAD ADMIN VARIABLES TO RUNTIME;
SAVE ADMIN VARIABLES TO DISK;

SHOW TABLES FROM monitor;
SELECT * FROM monitor.mysql_server_connect_log ORDER BY time_start_us DESC LIMIT 3;


SHOW CREATE TABLE mysql_replication_hostgroups\G
INSERT INTO mysql_replication_hostgroups (writer_hostgroup,reader_hostgroup,comment) VALUES (1,2,'cluster1');
LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;
SELECT * FROM monitor.mysql_server_read_only_log ORDER BY time_start_us DESC LIMIT 3;

<!--UPDATE mysql_servers SET hostgroup_id = 2 WHERE hostname IN ('172.88.88.13', '172.88.88.14');-->

SELECT * FROM mysql_servers;



SHOW CREATE TABLE mysql_users\G

INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('root','password',1);
INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('fish','password',1);


LOAD MYSQL VARIABLES TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;

SELECT * FROM mysql_users;

LOAD MYSQL USERS TO RUNTIME;
SAVE MYSQL USERS TO DISK;
LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL QUERY RULES TO DISK;
LOAD MYSQL VARIABLES TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;
LOAD ADMIN VARIABLES TO RUNTIME;
SAVE ADMIN VARIABLES TO DISK;

```

```angular2html
mysql -u fish -ppassword -h 172.88.88.100 -P6033 -e"SELECT @@port"
mysql -u fish -ppassword -h 172.88.88.100 -P6033 --prompt 'FISH > '

sysbench --db-driver=mysql --mysql-host=172.88.88.103 --mysql-port=3306 --mysql-user=fixh --mysql-password=password --mysql-db=fishfish --table-size=1000000 --tables=10 --threads=5 --time=300 --events=0 oltp_point_select prepare
sysbench --db-driver=mysql --mysql-host=172.88.88.100 --mysql-port=6033 --mysql-user=fish --mysql-password=password --mysql-db=fishfish --table-size=1000000 --tables=10 --threads=5 --time=300 --events=0 oltp_point_select run > report.txt


```

# proxysql 查询
```
## 查询每个节点的使用状况、链接数量等
SELECT * FROM stats.stats_mysql_connection_pool;
## 查询各种sql操作的数量
SELECT * FROM stats_mysql_commands_counters WHERE Total_cnt;
```