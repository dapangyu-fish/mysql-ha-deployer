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
docker run -p --net mynetwork --ip 172.88.88.2 16032:6032 -p 16033:6033 -p 16070:6070 -d --restart=always --name=proxysql proxysql/proxysql
```

```docker deploy mysql
docker run --net mynetwork --ip 172.88.88.3 --restart=always --name mysql-master -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --net mynetwork --ip 172.88.88.4 --restart=always --name mysql-slave-1 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --net mynetwork --ip 172.88.88.5 --restart=always --name mysql-slave-2 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
```

```in proxysql
docker exec -it proxysql bash
mysql -u admin -padmin -h proxysql -P6032 --prompt 'ProxySQL Admin> '
```
