# How to use

## Setup

First you need to clone 3 repositories into this (the direcetory that this README is in) directory.

1. git@github.com:elastic/elasticsearch.git
2. git@github.com:elastic/elasticsearch-py.git
3. git@github.com:elastic/elasticsearch-dsl-py.git

## Install Docker and Docker Compose

https://docs.docker.com/engine/installation/

If you are installing Docker for Mac or Docker For Windows it will inclue installing Docker Compose.
If you are installing Docker on a Linux machine you will need to also install Docker Compose.

## Building

Build the images

```bash
$ make build
```

To build individual elasticsearch python client images:

```bash
export PYTHON_VERSION=3 && docker build --build-arg VERSION=$PYTHON_VERSION -t fxdgear/elasticsearch-py:$PYTHON_VERSION .
```

## Starting ElasticSearch

```bash
$ make up
```

## Run the tests

```bash
$ make test-client
```

## Other tips and tricks

Sometimes it is helpful to want to run some python code or execute a single test or just "hop on to the machine".
There's a make target:

```bash
$ make client-bash
```

This will create a new container with a bash prompt at which you can run `ipython` or what ever.
You can connect to the ES instance with something like:

```
In [1]: from elasticsearch import Elasticsearch

In [2]: es = Elasticsearch('elasticsearch')

In [3]: es.ping()
Out[3]: True

In [4]:
```

Please note that the domain for elasticsearch is `elasticsearch` and **not** `localhost`.



