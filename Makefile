THIS_FILE := $(lastword $(MAKEFILE_LIST))

build-elasticsearch:
	docker build --build-arg ELASTIC_VERSION=$(ELASTIC_VERSION) -t fxdgear/elasticsearch:$(ELASTIC_VERSION) -f elasticsearch/Dockerfile ./elasticsearch

build-elasticsearch-xpack: build-elasticsearch
	docker build --build-arg ELASTIC_VERSION=$(ELASTIC_VERSION) -t fxdgear/elasticsearch:$(ELASTIC_VERSION)-xpack -f elasticsearch/Dockerfile.xpack .

build-kibana:
	docker build --build-arg ELASTIC_VERSION=$(ELASTIC_VERSION) -t fxdgear/kibana:$(ELASTIC_VERSION) -f kibana/Dockerfile .

build-kibana-xpack: build-kibana
	docker build --build-arg ELASTIC_VERSION=$(ELASTIC_VERSION) -t fxdgear/kibana:$(ELASTIC_VERSION)-xpack -f kibana/Dockerfile.xpack .

build-logstash:
	docker build --build-arg ELASTIC_VERSION=$(ELASTIC_VERSION) -t fxdgear/logstash:$(ELASTIC_VERSION) -f logstash/Dockerfile .

build-logstash-xpack:
	docker build --build-arg ELASTIC_VERSION=$(ELASTIC_VERSION) -t fxdgear/logstash:$(ELASTIC_VERSION)-xpack -f logstash/Dockerfile.xpack .

build-stack: build-elasticsearch build-kibana build-logstash
	@echo "done"




golang:
	cd logstash; docker build -t golang:env2yaml build/golang

# Compile "env2yaml", the helper for configuring logstash.yml via environment
# variables.
env2yaml: golang
	cd logstash; docker run --rm -i \
	  -v ${PWD}/logstash/build/env2yaml:/usr/local/src/env2yaml \
	  golang:env2yaml

build-es-5.5.0:
	export ELASTIC_VERSION=5.5.0 && $(MAKE) -f $(THIS_FILE) build-elasticsearch

build-es-5.4.0:
	export ELASTIC_VERSION=5.4.0 && $(MAKE) -f $(THIS_FILE) build-elasticsearch

build-es-5.3.0:
	export ELASTIC_VERSION=5.3.0 && $(MAKE) -f $(THIS_FILE) build-elasticsearch

build-es-2.4.0:
	export ELASTIC_VERSION=5.3.0 && $(MAKE) -f $(THIS_FILE) build-elasticsearch


###
# Ignore everything below
####
run-elasticsearch:
	docker-compose -f elasticsearch-5.4/docker-compose.yml up -d
run-elasticsearch53:
	docker-compose -f elasticsearch-5.3/docker-compose.yml up -d
run-elasticsearch24:
	docker-compose -f elasticsearch-2.4/docker-compose.yml up -d



es-stack-24:
	docker-compose -f elasticsearch-2.4/docker-compose.yml -f kibana-4.6/docker-compose.yml up -d

es-stack-53:
	docker-compose -f elasticsearch-5.3/docker-compose.yml -f kibana-5.3/docker-compose.yml up -d

es-stack-54:
	docker-compose -f elasticsearch-5.4/docker-compose.yml -f kibana-5.4/docker-compose.yml up -d

