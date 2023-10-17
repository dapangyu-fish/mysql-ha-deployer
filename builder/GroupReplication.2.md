# mysql-ha-deployer
- create bridge
```create bridge
docker network create --subnet=172.88.88.0/24 ha-mysql
```
- clean all
```clean all


docker rm -f mysql1
docker rm -f mysql2
docker rm -f mysql3
docker run --hostname mysql1 --net ha-mysql --ip 172.88.88.103 --restart=always --name mysql1 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 mysql:8.0.23
docker run --hostname mysql2 --net ha-mysql --ip 172.88.88.104 --restart=always --name mysql2 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 mysql:8.0.23
docker run --hostname mysql3 --net ha-mysql --ip 172.88.88.105 --restart=always --name mysql3 -e MYSQL_ROOT_PASSWORD=password -d --add-host=mysql1:172.88.88.103 --add-host=mysql2:172.88.88.104 --add-host=mysql3:172.88.88.105 mysql:8.0.23

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
group_replication_bootstrap_group=off
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

```angular2html
echo "172.88.88.103	mysql1">>/etc/hosts
echo "172.88.88.104	mysql2">>/etc/hosts
echo "172.88.88.105	mysql3">>/etc/hosts
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
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061"
group_replication_bootstrap_group=off
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
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061"
group_replication_bootstrap_group=off
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

set global group_replication_ip_allowlist="172.88.88.103,172.88.88.104,172.88.88.105";
CHANGE MASTER TO MASTER_USER='rpl_user', MASTER_PASSWORD='Rpl_user123' FOR CHANNEL 'group_replication_recovery';

START GROUP_REPLICATION;

SELECT * FROM performance_schema.replication_group_members;


```
