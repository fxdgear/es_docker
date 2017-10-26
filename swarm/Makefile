# Cert gen command takes in the `instances.yml` file and creates a bundle.zip with certs
certgen:
	docker run --user root -v `pwd`:/tmp --rm -it fxdgear/elasticsearch:6.0.0-rc1 ./bin/x-pack/certgen -in /tmp/instances.yml -out /tmp/bundle.zip

# Clear all docker secrets
clear_secrets:
	docker secret rm $(docker secret ls -q)
