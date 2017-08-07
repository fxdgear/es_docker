# Elasticsearch in Swarm Mode

First create a docker swarm:

```
$ docker swarm init
```

Next you want to `deploy` the ES service

```
$ docker stack deploy -c docker-compose.yml elasticsearch
```

Now if you want to scale the number of data nodes...

```
$ docker service scale elasticsearch=3
```
