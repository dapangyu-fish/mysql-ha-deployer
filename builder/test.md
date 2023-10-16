# mysql-ha-deployer
- create bridge
```create bridge
docker network create --subnet=172.88.88.0/24 ha-mysql
```
- clean all
```clean all
docker rm -f proxysql
docker rm -f mysql-master
docker rm -f mysql-slave-1
docker rm -f mysql-slave-2
```
- deploy proxysql
```docker deploy proxysql
docker run --net ha-mysql --ip 172.88.88.2 -p 16032:6032 -p 16033:6033 -p 16070:6070 -d --restart=always --name=proxysql proxysql/proxysql
```

```docker deploy mysql
docker run --net ha-mysql --ip 172.88.88.3 --restart=always --name mysql-master -e MYSQL_ROOT_PASSWORD=password -d mysql:5.6
docker run --net ha-mysql --ip 172.88.88.4 --restart=always --name mysql-slave-1 -e MYSQL_ROOT_PASSWORD=password -d mysql:5.6
docker run --net ha-mysql --ip 172.88.88.5 --restart=always --name mysql-slave-2 -e MYSQL_ROOT_PASSWORD=password -d mysql:5.6
```

```in proxysql
docker exec -it proxysql bash

mysql -u admin -padmin -h 127.0.0.1 -P6032 --prompt 'ProxySQL Admin> '

SELECT * FROM mysql_servers;
SELECT * from mysql_replication_hostgroups;
SELECT * from mysql_query_rules;

INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.3',3306);
INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.4',3306);
INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'172.88.88.5',3306);
SELECT * FROM mysql_servers;
```

```in mysql
docker exec -it mysql-master bash

mysql -u root -ppassword

SET GLOBAL read_only = 0;
CREATE USER 'monitor'@'%' IDENTIFIED BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
exit
exit

docker exec -it mysql-slave-1 bash

mysql -u root -ppassword

SET GLOBAL read_only = 1;
CREATE USER 'monitor'@'%' IDENTIFIED BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
exit
exit

docker exec -it mysql-slave-2 bash

mysql -u root -ppassword

SET GLOBAL read_only = 1;
CREATE USER 'monitor'@'%' IDENTIFIED BY 'monitor';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
exit
exit
```

```in proxysql
docker exec -it proxysql bash
mysql -u admin -padmin -h 127.0.0.1 -P6032 --prompt 'ProxySQL Admin> '
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
SELECT * FROM monitor.mysql_server_read_only_log ORDER BY time_start_us DESC LIMIT 3;

UPDATE mysql_servers SET hostgroup_id = 2 WHERE hostname IN ('172.88.88.4', '172.88.88.5');

SELECT * FROM mysql_servers;



SHOW CREATE TABLE mysql_users\G

INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('root','',1);
INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('stnduser','stnduser',1);

LOAD MYSQL VARIABLES TO RUNTIME;
SAVE MYSQL VARIABLES TO DISK;
```

```angular2html
mysql -u stnduser -pstnduser -h 172.88.88.2 -P6033

sysbench --report-interval=5 --num-threads=4 --num-requests=0 --max-time=20 --test=tests/db/oltp.lua --mysql-user='stnduser' --mysql-password='stnduser' --oltp-table-size=10000 --mysql-host=172.88.88.2 --mysql-port=6033 run

```