#!/bin/bash

docker secret create master.key master/master.key
docker secret create master.crt master/master.crt

docker secret create elasticsearch.key elasticsearch/elasticsearch.key
docker secret create elasticsearch.crt elasticsearch/elasticsearch.crt

docker secret create ca.key ca/ca.key
docker secret create ca.crt ca/ca.crt
