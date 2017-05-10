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

## How To Use

Lets make sure that ES is healthy.

```
$ docker ps

CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS                     PORTS                                                    NAMES
62ffbb76f7cf        fxdgear/kibana:5.3          "/docker-entrypoin..."   8 minutes ago       Up 8 minutes (healthy)     5601/tcp                                                 elasticsearch53_kibana_1
b47276e4a976        nginx:1                     "/bin/bash -c 'ech..."   8 minutes ago       Up 8 minutes               0.0.0.0:5601->5601/tcp, 80/tcp, 0.0.0.0:9200->9200/tcp   elasticsearch53_nginx_1
e6204accab1d        fxdgear/elasticsearch:5.3   "/docker-entrypoin..."   8 minutes ago       Up 8 minutes (healthy)     9200/tcp, 9300/tcp                                       elasticsearch53_elasticsearch_1
```

You should see a `(healthy)` in the `STATUS` column.

You can now access [`http://localhost:9200`](http://localhost:9200) and see that the ES cluster is responding.
You can now access [`http://localhost:5601`](http://localhost:5601) and see that the Kibana is responding.
