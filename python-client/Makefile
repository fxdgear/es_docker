client2-bash:
	docker-compose run --rm client2 bash
client3-bash:
	docker-compose run --rm client3 bash
dsl-bash:
	docker-compose run --rm dsl-client bash
build:
	docker-compose build --pull --force-rm --no-cache
up:
	docker-compose up -d

test-client3:
	docker-compose run client3 python setup.py test
test-client2:
	docker-compose run client2 python setup.py test
test-dsl-client:
	docker-compose run dsl-client python setup.py test
clean:
	docker-compose down --rmi local -v --remove-orphans

load-example-data:
	docker-compose run client python example/load.py -H elasticsearch:9200
