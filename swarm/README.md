# Elasticsearch 6 in Swarm Mode with SSL/TLS

Deploying Elasticsearch 6 in swarm mode is a fairly heafty task. My goal is to help understand
the nessisary steps required to make this happen.

The first step, obviously, is to create a docker swarm:

```
$ docker swarm init
```

## SSL Certificates

Once we have our swarm created the next step is create some SSL certs for our cluster. In
Elasticsearch 6 while using X-Pack, SSL is required.

To create an SSL cert we can use the [Certgen](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/certgen.html)
tool bundled with Elasticsearch.

When using the `certgen` tool you can specify an input file for an automated create of certs.
Or you can just run the tool with 0 parameters and use it interactivly. For this example
we are going to privde an `instances.yml` file with our predefined instances for certs.

```yaml
instances:
  - name: "docker-cluster"
    dns:
      - "*"
      - "master"
      - "elasticsearch"

```

What is this file doing? Well it's going to create a CA cert and key. It's also going to create
a server cert and key which can auth against a self signed cert. This server's key is going to be called
`docker-cluster`. The SSL keys will have 3 SANs (Subject Alternative Names).

* `*`
* `master`
* `elasticsearch`

The first is a wild card. This means any dns name will be valid. Please note that this is not the most secure way
of doing things. So please if any smarter people than me are around and can help solve this issue i'd be eternally
greatful.

The last two SANs are `master` and `elasticsearch`  in our docker stack file we will have 2 services though we can always make more.
We will just have to create new certs.
The `master` service will be both a data and master node.
The `elasticsearch` service will be a dedicated coordinating node (aka a client node). More on this later.

Now lets actually create our certs:

```bash
docker run --user root -v `pwd`:/tmp --rm -it fxdgear/elasticsearch:6.0.0-rc1 ./bin/x-pack/certgen -in /tmp/instances.yml -out /tmp/bundle.zip
```

Lets look at what is happening in this docker command.

First: `docker run --user root`. This part of the command says we want to run the container with the `root` user. This way
we have permission to access the `/tmp` directory for read and write. (Note to self we might want to change this to get rid of
`root` and change the volume mount to be `/user/share/elasticsearch/x-pack` this way we avoid permissions problems.

The next section is `-v `pwd`:/tmp` this part of the command is going to specify the location where we want our `instances.yml` file to
be mounted into the container and read by the certgen tool.

The next section `--rm -it` means we want to delete this container as soon as it exits and
we also want to privde input and teletype.

Next `docker.elastic.co/elasticsearch:6.0.0-rc1` is the image we want to run our container from.

And finally `./bin/x-pack/certgen -in /tmp/instances.yml -out /tmp/bundle.zip` is the command
we want to run inside the container. This will accept our `instances.yml` file and create a
`bundle.zip` file which we can extract to get our cert info from.

> As a note, the bundle.zip file will be owned by the `root` user. So you might have to

```bash
sudo chown `whoami`:`whoami` bundle.zip
```

Now we can `unzip bundle.zip` and view our certs. If you navigate to the `docker-cluster`
directory you can run the following command:

```bash
openssl x509 -text -in bundle/docker-cluster/docker-cluster.crt
```

And you should be able to see the three SAN we have for this sert:

```
X509v3 Subject Alternative Name:
    DNS:*, DNS:master, DNS:elasticsearch

```

## Docker Secrets

The next step is to load the certs into Docker [Secrets](https://docs.docker.com/engine/swarm/secrets/).

Loading the certs and keys into Elasticsearch is pretty simple we just need to run a few commands:

```bash

$ docker secret create ca.crt ca/ca.crt
$ docker secret create docker-cluster.crt docker-cluster/docker-cluster.crt
$ docker secret create docker-cluster.key docker-cluster/docker-cluster.key
```

Now we have our CA cert and our server cert and keys loaded into docker secrets. These
secrets can now be access by services (containers) that have been given access to these
secrets. We will look at how to use these secrets in the next section.

## Docker Stack Deploy

Now that all this prep work has been done we need to actually deploy something.
The easiest way to do that is by using a docker stack file. Lets look at one:

```yaml
version: "3.4"
services:
  # coordinating node. Used for Load balancing across containers
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:6.0.0-rc1
    environment:
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    networks:
       - esnet
    volumes:
      - esdata:/usr/share/elasticsearch/data
    ports:
      - target: 9200
        published: 9200
        protocol: tcp
        mode: host
    deploy:
      endpoint_mode: dnsrr
      mode: 'global'
      resources:
        limits:
          memory: 1G
    secrets:
      - source: elasticsearch.yml
        target: /usr/share/elasticsearch/config/elasticsearch.yml
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: docker-cluster.key
        target: /usr/share/elasticsearch/config/x-pack/docker-cluster/docker-cluster.key
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: docker-cluster.crt
        target: /usr/share/elasticsearch/config/x-pack/docker-cluster/docker-cluster.crt
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: ca.crt
        target: /usr/share/elasticsearch/config/x-pack/ca/ca.crt
        uid: '1000'
        gid: '1000'
        mode: 0440

  master:
    image: docker.elastic.co/elasticsearch/elasticsearch:6.0.0-rc1
    environment:
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    networks:
       - esnet
    volumes:
      - esdata:/usr/share/elasticsearch/data
    deploy:
      endpoint_mode: dnsrr
      mode: 'replicated'
      replicas: 2
      resources:
        limits:
          memory: 1G
    secrets:
      - source: master.yml
        target: /usr/share/elasticsearch/config/elasticsearch.yml
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: docker-cluster.key
        target: /usr/share/elasticsearch/config/x-pack/docker-cluster/docker-cluster.key
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: docker-cluster.crt
        target: /usr/share/elasticsearch/config/x-pack/docker-cluster/docker-cluster.crt
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: ca.crt
        target: /usr/share/elasticsearch/config/x-pack/ca/ca.crt
        uid: '1000'
        gid: '1000'
        mode: 0440

  kibana:
    image: docker.elastic.co/kibana/kibana:6.0.0-rc1
    command: "/usr/share/kibana/bin/kibana --cpu.cgroup.path.override=/ --cpuacct.cgroup.path.override=/ -c /usr/share/kibana/config/kibana.yml -c /usr/share/kibana/config/password.yml --elasticsearch.url=https://elasticsearch:9200"
    networks:
      - esnet
    ports:
      - target: 5601
        published: 5601
        protocol: tcp
        mode: host
    volumes:
      - ./kibana:/etc/kibana
    deploy:
      resources:
         limits:
           memory: 1G
    secrets:
      - source: kibana_password
        target: /usr/share/kibana/config/password.yml
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: kibana.yml
        target: /usr/share/kibana/config/kibana.yml
        uid: '1000'
        gid: '1000'
        mode: 0440
      - source: ca.crt
        target: /usr/share/kibana/config/x-pack/ca/ca.crt
        uid: '1000'
        gid: '1000'
        mode: 0440

secrets:
  ca.crt:
    external: true
  docker-cluster.crt:
    external: true
  docker-cluster.key:
    external: true
  master.yml:
    external: true
  kibana.yml:
    external: true
  elasticsearch.yml:
    external: true
  elastic_password:
    external: true
  kibana_password:
    external: true
  logstash_password:
    external: true


volumes:
  esdata:
    driver: local
networks:
  esnet:
    driver: overlay
```

Holy cow that's huge right? Well it's doing a lot of work for us that we would normally have to
use docker services for. Lets break this file down so we can understand whats going on. We will
work our way from top level definitons to lower level definitions and then top down. As opposed to just plain
top down.

Our top level defitions are `version`, `services`, `secrets`, `volumes` and `networks`.
Lets look at these in order.

1. `version`: We are using docker-compose syntax version 3.4. Which as of the time of this
writing is the latest version of docker-compose syntax
2. `services`: Services is where we define all the services we want deployed in our stack. We
will get a bit deeper into these in a bit.
3. `secrets`: These are the secrets we want our `stack` to have access too. If we don't list the secrets
we want here. Then our containers (services) will not be able to read these secrets.
4. `volumes`: This is where we can define volumes to help persist our data.
5. `networks`: This is where we define the network we want our services to communicate over. It's
a nice way to isolate communication between our elastic cluster so it doesn't interfear with any other
services we might have running in our swarm cluster.

That was pretty simple right. So now lets go down a level and look at our `services` we have defined:

First we have our `elasticsearch` service. This service is our dedicated coordinating
node. Otherwise known as a client node for those of you who come from older versions of
Elasticsearch. A dedicated coordinating node acts as a load balancer. And more
specifically in an Elasticsearch cluster we want to expose port 9200 for clients to
connect to our cluster. If there happen to be multiple ES instances running on a single
swarm node, only one of those esrvices can expose port 9200 at a time. So we can use
the dedicated coordinating node as our "entry point" into the ES cluster.

So now lets go line by line in this service defintion to understand what's going on.

* `image`: the docker image we want to use for our serivce
* `environment`: here we are defining any env vars and specifically our heap settings
* `networks`: the network we want to use for this service
* `volumes`: the volume we want to use and where to mount it inside the container
* `ports`: as mentioned above we want this port to be external exposed
* `deploy`: This is where we set constraints for deploy time
    * `endpoint_mode`: instead of using `vip` by default we are going to use dns round robin.
    * `mode`: global mode means only one instances of this service can exist on each swarm host.
    * `resources`: this is where we limit cpu and ram etc avail to the container
* `secrets`: This is where we give access to specific sercrets for this service.

Our next service is `master`. In this example our master node is also a data node,
but we can similarly define a `data` service as well, if we wanted to have
dedicated master nodes. If we were to have a dedicated master node we would want to
set the `mode` to `global` as well. So we ensure that our master nodes are 1:1 with
swarm nodes to ensure losing a swarm node doesn't take out multiple master nodes.
The settings in our master service is pretty similar to our elasticsearch service so
I'll just highlight some of the differences.

1. our deploy mode is `replicated` as opposed to `global`, which means multiple
services can be running on a single swarm node.

## Elasticsearch Config

So the purpose of using the offical Elasticsearch image is that as a consumer you
don't need to maintain your own image on top of ours. We don't want you to have to
maintain an elasticsearch.yml AND a Dockerfile which goes through the process of
adding certs and configs into the images. On top of that, changing a cert, or
a config setting shouldn't require a new build of a docker image.

So the same way we created the secrets for our certs we can do the same thing for our
elasticsearch configs. This allows us to keep in version control our configs,
and keep them sepreate from the artifact that gets deployed to production.

After we've added our elasticsearch configs to docker secrets:

```
$ docker secret create elasticsearcy.yml elasticsearch/config/elasticsearch.yml
$ docker secret create master.yml elasticsearch/config/master.yml
```

We can sepcify where in the container this secret will be mounted and the permissions
on the file so that the elasticsearch user can read this file.

```yaml
      - source: master.yml
        target: /usr/share/elasticsearch/config/elasticsearch.yml
        uid: '1000'
        gid: '1000'
        mode: 0440
```


I'm sure you noticed that, I've skipped over until now, in our secrets we are using
`elasticsearch.yml` as a secret. Where did that come from?

Lets look at our `elasticsearch.yml`:

```yaml
discovery.zen.minimum_master_nodes: 2
discovery.zen.ping.unicast.hosts: master
bootstrap.memory_lock: false
node.master: false
node.data: false
node.ingest: false
node.max_local_storage_nodes: 3
xpack.ssl.key: /usr/share/elasticsearch/config/x-pack/docker-cluster/docker-cluster.key
xpack.ssl.certificate: /usr/share/elasticsearch/config/x-pack/docker-cluster/docker-cluster.crt
xpack.ssl.certificate_authorities: /usr/share/elasticsearch/config/x-pack/ca/ca.crt
xpack.security.transport.ssl.enabled: true
xpack.security.http.ssl.enabled: true
network.bind_host: 0.0.0.0
network.publish_host: ${HOSTNAME}
```


A couple things to note about this file, this is the config for our dedicated
coordinating node so we have set: `node.master`, `node.data` and `node.ingest`
to `false`

We are also setting the `node.max_local_storage_nodes` to 3. Because we have
3 total nodes in this cluster. They are all accessing the same
`volume`. So we want ES to know to split up the directory where persistant
data is stored so different ES processes can have their own data directory.

We are also specifying the location for our ssl key, ssl cert and certificat authorities.
These values have to match the paths specified in our `secrets` section of
the `elasticsearch` service.

We are also enabling SSL on HTTP and transport layers.
We are setting the `bind_host` to `0.0.0.0` and the `publish_host` to the hostname
of the container. Binding to 0.0.0.0 allows each node to communicate "globally" and by
setting the `publish_host` to hostname we can publish our self to a value that's not
an IP address. This is required becauze the SAN we were talking about at the begining
is going to be validated against the hostname.

If we look at the `master.yml` the only differences will be `node.master: true` and
`node.data: true`. This will make sure our cluster runs and discovers itself and
a master election can occur.



## Kibana

Our next service is Kibana. Now that we've done so much work digging into the guts
of the elasticsearch services the kibana one should be pretty straight forward, with
a couple minor differences.

With kibana we want to add some secrets like our ca and our kibana.yml and password.yml

Wait, what's `password.yml`.

With Elasticsearch 6 the default `changeme` password is going away. So we will have to
generate some passwords for the users `elastic`, `kibana` and `logstash`.

In order to create these passwords we need to use the password generation tool that
is bundled with Elastic search. Unfortunalty we can't just do a docker run to do this now.

So first we are going to have to deploy our stack:

```
$ docker stack deploy -c docker-compose.yml elasticsearch
```

After our stack has deployed you should be able to run `docker ps` and see a list of
containers:

```
CONTAINER ID        IMAGE                                                     COMMAND                  CREATED             STATUS              PORTS                              NAMES
9e62aa29d29f        docker.elastic.co/elasticsearch/elasticsearch:6.0.0-rc1   "/bin/bash bin/es-..."   18 hours ago        Up 18 hours         0.0.0.0:9200->9200/tcp, 9300/tcp   elasticstack_elasticsearch.iol21z1h8a84b0ixgivkmqxyk.5mnr6eps826fz2yid3tmhfpok
588d34263552        docker.elastic.co/kibana/kibana:6.0.0-rc1                 "/usr/share/kibana..."   18 hours ago        Up 18 hours         0.0.0.0:5601->5601/tcp             elasticstack_kibana.1.fe5qchct688fkkmjn5rhgoevi
c83918083ef3        docker.elastic.co/elasticsearch/elasticsearch:6.0.0-rc1   "/bin/bash bin/es-..."   18 hours ago        Up 18 hours         9200/tcp, 9300/tcp                 elasticstack_master.2.uo4r1na13ivmjtvyx6omp2iq8
e3e945b5c2f2        docker.elastic.co/elasticsearch/elasticsearch:6.0.0-rc1   "/bin/bash bin/es-..."   18 hours ago        Up 18 hours         9200/tcp, 9300/tcp                 elasticstack_master.1.l1lz45fma7pghwk9oiu6heuo4
```

Now copy the container ID of one of the `master` nodes and we will want to exec into that container.

```
docker exec -it e3e945b5c2f2 bash
```

From within the container we will run the command:

```
./bin/x-pack/setup-passwords auto -u https://elasticsearch:9200
```

This will output your passwords, make sure to copy and save these passwords.
You should put them into docker secrets.

To put a secret into docker secrets from stdin you would run this command:

```
echo '<kibana_password>' | docker secret create kibana_password -
```

Do this for elastic and logstash passwords as well.

Now back to Kibana and our `password.yml` file. Because Docker secrets stores secrets on
the filesystem in the container and not as env vars (it's more secure this way). We need
a way for kibana to access the value stored in the password file. Luckily for us Kibana
will accept multiple config files. You can specify as many `-c /path/to/config.yml` as you want.

So a hack to get around the fact that a yaml file can't read another yaml file we'll just
inject our kibana password into the container as a secret that is a yaml file.

so now we can create a new kibana secret

```
echo 'elasticsearch.password: <kibana_password>' | docker secret create password.yml -
```

Now if you notice in our serets definition for the kibana service there is a kibana.yml
as well as a password.yml and they both sitting in the same directory.

The next thing to note about our kibana service is the command is being overridden.

This is on purpose because we don't want to accept env vars as CLI parameters to kibana and
instead we want to pass in multiple config files.

So looking at what the command and entry point for the offical kibana image are I've just copied that
and added passing in 2 different config paths.

```
    command: "/usr/share/kibana/bin/kibana --cpu.cgroup.path.override=/ --cpuacct.cgroup.path.override=/ -c /usr/share/kibana/config/kibana.yml -c /usr/share/kibana/config/password.yml --elasticsearch.url=https://elasticsearch:9200"

```

Now if we deploy our stack again, to take into accout our new changes:

```
docker stack deploy -c docker-compose.yml elasticstack
```

We sould be able to wait a few moments before Kibana is up and running and authenticated against
elasticsearch.

Now you remembered to write down your `elastic` password right?

When you want to log into Kibana you'll need to log in using:

* username: `elastic`
* password: `<elastic_password>`

And there you go now you have Elasticsearch 6 running in swarm mode with X-Pack and SSL

