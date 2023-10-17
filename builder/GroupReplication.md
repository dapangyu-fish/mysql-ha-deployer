# mysql-ha-deployer
- create bridge
```create bridge
docker network create --subnet=172.88.88.0/24 ha-mysql
```
- clean all
```clean all
docker rm -f proxysql
docker rm -f mysql-1
docker rm -f mysql-2
docker rm -f mysql-3
docker rm -f mysql-4
docker rm -f mysql-5
```
- deploy proxysql
```docker deploy proxysql
docker run --net ha-mysql --ip 172.88.88.102 -p 16032:6032 -p 16033:6033 -p 16070:6070 -d --restart=always --name=proxysql-g proxysql/proxysql
```

```docker deploy mysql
docker run --net ha-mysql --ip 172.88.88.103 --restart=always --name mysql-1 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --net ha-mysql --ip 172.88.88.104 --restart=always --name mysql-2 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --net ha-mysql --ip 172.88.88.105 --restart=always --name mysql-3 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --net ha-mysql --ip 172.88.88.106 --restart=always --name mysql-4 -e MYSQL_ROOT_PASSWORD=password -d -v /home/zhaoyihuan/mysqlMGR/mysql-4/my.cnf:/etc/my.cnf mysql:latest
docker run --net ha-mysql --ip 172.88.88.107 --restart=always --name mysql-5 -e MYSQL_ROOT_PASSWORD=password -d -v /home/zhaoyihuan/mysqlMGR/mysql-5/my.cnf:/etc/my.cnf mysql:latest

```

# https://blog.csdn.net/wzy0623/article/details/95619837

- mysql-1
```
docker exec -it mysql-1 bash

mysql -u root -ppassword

install plugin group_replication soname 'group_replication.so';

exit

cat <<EOF >> /etc/my.cnf
[mysqld]
server_id=1125
gtid_mode=ON
enforce-gtid-consistency=true
binlog_checksum=NONE
innodb_buffer_pool_size=4G
 
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
 
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
 
transaction_write_set_extraction=XXHASH64
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.103:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061"
group_replication_bootstrap_group=off
EOF

CREATE USER 'replicate_user'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'replicate_user'@'%';
flush privileges;

CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';
CREATE USER 'stnduser'@'%' IDENTIFIED WITH mysql_native_password BY 'stnduser';
GRANT ALL PRIVILEGES ON *.* TO 'stnduser'@'%';

reset master;		
show master status;

## set slave from master-2
stop slave;
reset slave;
change master to master_host='172.88.88.4',master_user='replicate_user',master_port=3306,master_password='password',master_log_file='mysql-bin.000001',master_log_pos=157;
start slave;
show slave status \G

exit
exit
```


- mysql-2
```
docker exec -it mysql-2 bash

mysql -u root -ppassword

install plugin group_replication soname 'group_replication.so';

exit

cat <<EOF >> /etc/my.cnf
[mysqld]
server_id=1126
gtid_mode=ON
enforce-gtid-consistency=true
binlog_checksum=NONE
innodb_buffer_pool_size=4G
 
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
 
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
 
transaction_write_set_extraction=XXHASH64
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.104:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061"
group_replication_bootstrap_group=off
EOF

exit
exit
```

- mysql-3
```
docker exec -it mysql-3 bash

mysql -u root -ppassword

install plugin group_replication soname 'group_replication.so';

exit

cat <<EOF >> /etc/my.cnf
[mysqld]
server_id=1127
gtid_mode=ON
enforce-gtid-consistency=true
binlog_checksum=NONE
innodb_buffer_pool_size=4G
 
disabled_storage_engines="MyISAM,BLACKHOLE,FEDERATED,ARCHIVE,MEMORY"
 
log_bin=binlog
log_slave_updates=ON
binlog_format=ROW
master_info_repository=TABLE
relay_log_info_repository=TABLE
 
transaction_write_set_extraction=XXHASH64
group_replication_group_name="3955DFE7-55C4-52B5-2283-1A90677C78B9"
group_replication_start_on_boot=off
group_replication_local_address= "172.88.88.105:33061"
group_replication_group_seeds= "172.88.88.103:33061,172.88.88.104:33061,172.88.88.105:33061"
group_replication_bootstrap_group=off
EOF

exit
exit

mysqladmin -uroot -ppassword shutdown
mysqld_safe --defaults-file=/etc/my.cnf &
```

- master-2
```
docker exec -it mysql-master-2 bash

mysql -u root -ppassword

SET GLOBAL read_only = 0;

CREATE USER 'replicate_user'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'replicate_user'@'%';
flush privileges;

CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';
CREATE USER 'stnduser'@'%' IDENTIFIED WITH mysql_native_password BY 'stnduser';
GRANT ALL PRIVILEGES ON *.* TO 'stnduser'@'%';

reset master;		
show master status;

## set slave from master-1
stop slave;
reset slave;
change master to master_host='172.88.88.3',master_user='replicate_user',master_port=3306,master_password='password',master_log_file='mysql-bin.000001',master_log_pos=157;
start slave;
show slave status \G

exit
exit
```

- slave-1
```
docker exec -it mysql-slave-1 bash

mysql -u root -ppassword

CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';
CREATE USER 'stnduser'@'%' IDENTIFIED WITH mysql_native_password BY 'stnduser';
GRANT ALL PRIVILEGES ON *.* TO 'stnduser'@'%';

stop slave;
reset slave;
change master to master_host='172.88.88.3',master_user='replicate_user',master_port=3306,master_password='password',master_log_file='mysql-bin.000001',master_log_pos=157;
start slave;
show slave status \G
SET GLOBAL read_only = 1;
set global super_read_only=1;
show global variables like '%read_only%';

exit
exit
```

- slave-2
```
docker exec -it mysql-slave-2 bash

mysql -u root -ppassword

CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';
CREATE USER 'stnduser'@'%' IDENTIFIED WITH mysql_native_password BY 'stnduser';
GRANT ALL PRIVILEGES ON *.* TO 'stnduser'@'%';

stop slave;
reset slave;
change master to master_host='172.88.88.4',master_user='replicate_user',master_port=3306,master_password='password',master_log_file='mysql-bin.000001',master_log_pos=157;
start slave;
show slave status \G
SET GLOBAL read_only = 1;
set global super_read_only=1;
show global variables like '%read_only%';

exit
exit
```


```in mysql
docker exec -it mysql-master-1 bash

mysql -u root -ppassword

SET GLOBAL read_only = 0;

CREATE USER 'replicate_user'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'replicate_user'@'%';
flush privileges;

CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';
CREATE USER 'stnduser'@'%' IDENTIFIED WITH mysql_native_password BY 'stnduser';
GRANT ALL PRIVILEGES ON *.* TO 'stnduser'@'%';

reset master;		
show master status;

exit
exit

docker exec -it mysql-slave-1 bash

mysql -u root -ppassword

CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';
CREATE USER 'stnduser'@'%' IDENTIFIED WITH mysql_native_password BY 'stnduser';
GRANT ALL PRIVILEGES ON *.* TO 'stnduser'@'%';

stop slave;
reset slave;
change master to master_host='172.88.88.3',master_user='replicate_user',master_port=3306,master_password='password',master_log_file='mysql-bin.000001',master_log_pos=157;
start slave;
show slave status \G
SET GLOBAL read_only = 1;
set global super_read_only=1;
show global variables like '%read_only%';

exit
exit

docker exec -it mysql-slave-2 bash

mysql -u root -ppassword

SET GLOBAL read_only = 1;
CREATE USER 'monitor'@'%' IDENTIFIED WITH mysql_native_password BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
CREATE USER 'fish'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'%';
CREATE USER 'stnduser'@'%' IDENTIFIED WITH mysql_native_password BY 'stnduser';
GRANT ALL PRIVILEGES ON *.* TO 'stnduser'@'%';

stop slave;
reset slave;
change master to master_host='172.88.88.4',master_user='replicate_user',master_port=3306,master_password='password',master_log_file='mysql-bin.000001',master_log_pos=157;
start slave;
show slave status \G
SET GLOBAL read_only = 1;
set global super_read_only=1;
show global variables like '%read_only%';

exit
exit


```

```in proxysql
docker exec -it proxysql bash
mysql -u admin -padmin -h 127.0.0.1 -P6032 --default-auth=mysql_native_password --prompt 'ProxySQL Admin> '
UPDATE global_variables SET variable_value='monitor' WHERE variable_name='mysql-monitor_username';
UPDATE global_variables SET variable_value='monitor' WHERE variable_name='mysql-monitor_password';
UPDATE global_variables SET variable_value='2000' WHERE variable_name IN ('mysql-monitor_connect_interval','mysql-monitor_ping_interval','mysql-monitor_read_only_interval');
SELECT * FROM global_variables WHERE variable_name LIKE 'mysql-monitor_%';

LOAD MYSQL VARIABLES TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;

SHOW TABLES FROM monitor;
SELECT * FROM monitor.mysql_server_connect_log ORDER BY time_start_us DESC LIMIT 3;


SHOW CREATE TABLE mysql_replication_hostgroups\G
INSERT INTO mysql_replication_hostgroups (writer_hostgroup,reader_hostgroup,comment) VALUES (1,2,'cluster1');
LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;
SELECT * FROM monitor.mysql_server_read_only_log ORDER BY time_start_us DESC LIMIT 3;

UPDATE mysql_servers SET hostgroup_id = 2 WHERE hostname IN ('172.88.88.13', '172.88.88.14');

SELECT * FROM mysql_servers;



SHOW CREATE TABLE mysql_users\G

INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('root','password',1);
INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('stnduser','stnduser',1);

INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('fish','password',1);


LOAD MYSQL VARIABLES TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;

SELECT * FROM mysql_users;
```
```angular2html
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
mysql -u fish -ppassword -h 172.88.88.2 -P6033 -e"SELECT @@port"
mysql -u fish -ppassword -h 172.88.88.2 -P6033 --prompt 'FISH > '
sysbench --report-interval=5 --num-threads=4 --num-requests=0 --max-time=20 --test=tests/db/oltp.lua --mysql-user='stnduser' --mysql-password='stnduser' --oltp-table-size=10000 --mysql-host=172.88.88.2 --mysql-port=6033 run



xxx

INSERT INTO mysql_query_rules (rule_id,active,username,match_digest,destination_hostgroup,apply) VALUES (10,1,'stnduser','^SELECT c FROM sbtest1 WHERE id=?',2,1);
INSERT INTO mysql_query_rules (rule_id,active,username,match_digest,destination_hostgroup,apply) VALUES (20,1,'stnduser','DISTINCT c FROM sbtest1',2,1);


```

```SELECE 全部到从节点
UPDATE mysql_users SET default_hostgroup=1; # by default, all goes to HG1
LOAD MYSQL USERS TO RUNTIME;
SAVE MYSQL USERS TO DISK; # if you want this change to be permanent
INSERT INTO mysql_query_rules (rule_id,active,match_digest,destination_hostgroup,apply)
VALUES
(1,1,'^SELECT.*FOR UPDATE$',1,1),
(2,1,'^SELECT',2,1);
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL QUERY RULES TO DISK; # if you want this change to be permanent
```


