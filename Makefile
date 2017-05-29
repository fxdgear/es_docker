
build: build-elasticsearch build-elasticsearch53 build-elasticsearch24

build-elasticsearch:
	docker-compose -f elasticsearch-5.4/docker-compose.yml build
build-elasticsearch53:
	docker-compose -f elasticsearch-5.4/docker-compose.yml build
build-elasticsearch24:
	docker-compose -f elasticsearch-5.4/docker-compose.yml build

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

