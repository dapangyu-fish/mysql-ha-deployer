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
docker run --net ha-mysql --ip 172.88.88.3 --restart=always --name mysql-master -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --net ha-mysql --ip 172.88.88.4 --restart=always --name mysql-slave-1 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --net ha-mysql --ip 172.88.88.5 --restart=always --name mysql-slave-2 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
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
```

```in mysql
docker exec -it mysql-master bash
mysql -u root -ppassword
CREATE USER 'monitor'@'%' IDENTIFIED BY 'password';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
exit
exit

docker exec -it mysql-slave-1 bash
mysql -u root -ppassword
CREATE USER 'monitor'@'%' IDENTIFIED BY 'password';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
exit
exit

docker exec -it mysql-slave-2 bash
mysql -u root -ppassword
CREATE USER 'monitor'@'%' IDENTIFIED BY 'password';
GRANT USAGE, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
exit
exit
```
