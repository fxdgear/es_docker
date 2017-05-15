es-24:
	docker-compose -f elasticsearch-2.4/docker-compose.yml -f kibana-4.6/docker-compose.yml up -d

es-53:
	docker-compose -f elasticsearch-5.3/docker-compose.yml -f kibana-5.3/docker-compose.yml up -d

es-54:
	docker-compose -f elasticsearch-5.4/docker-compose.yml -f kibana-5.4/docker-compose.yml up -d
