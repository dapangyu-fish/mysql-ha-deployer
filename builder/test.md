# mysql-ha-deployer
- deploy proxysql
```docker deploy proxysql
docker run -p 16032:6032 -p 16033:6033 -p 16070:6070 -d --restart=always --name=proxysql proxysql/proxysql
```

```docker deploy mysql
docker run --restart=always --name mysql-master -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --restart=always --name mysql-slave-1 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker run --restart=always --name mysql-slave-2 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
```

