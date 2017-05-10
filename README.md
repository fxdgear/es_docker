# Docker related Elasticsearch goodness

## Setup

In each `elasticsearch-X` directory is a dockerfile and docker-compose file for creating
and running an elastic cluster in docker.

To run an elastic search cluster you can do it either in swarm mode or not.


### Swarm Mode

To run elastic search in swarm mode first you need to init your swarm.

```
docker swarm init
```

Once your swarm is created you can deploy elastic search by running

```
docker stack deploy --compose-file docker-compose.yml elasticsearch
```

This will deploy one node. If you want more nodes just run

```
docker service scale elasticsearch_elasticsearch=X  # X = number of nodes
```

### Normal Mode

To run elasticsearch in normal mode just run

```
docker-compose up -d
```

## How to use

Lets make sure that ES is healthy.

```
$ docker ps

CONTAINER ID        IMAGE                         COMMAND                  CREATED             STATUS                    PORTS                            NAMES
d96fbbcbc909        nginx:1                       "/bin/bash -c 'ech..."   20 minutes ago      Up 20 minutes             80/tcp, 0.0.0.0:9200->9200/tcp   elasticsearch_nginx_1
3cf9e2564053        fxdgear/elasticsearch:5.3.0   "/docker-entrypoin..."   20 minutes ago      Up 20 minutes (healthy)   9200/tcp, 9300/tcp               elasticsearch_elasticsearch_1
```

You should see a `(healthy)` in the `STATUS` column.

You can now acess [`http://localhost:9200`](http://localhost:9200) and see that the ES cluster is responding.
