.PHONY = init install clean test venv

PROJECT ?= kuleuven/collective.amqpindexing
TAG     ?= latest
IMAGE=$(PROJECT):$(TAG)

bin/buildout=bin/buildout -Nt 4
bin/instance=bin/instance fg

venv: 
	@if test -f bin/python; then echo "Virtualenv already created"; \
		else virtualenv-2.7 --no-setuptools . ; fi

bootstrap: 
	@if test -f 'bootstrap.py'; then echo "bootstrap.py already downloaded"; \
		else wget http://downloads.buildout.org/2/bootstrap.py; fi
	@if test -f 'bin/buildout'; then echo "bin/buildout already generated"; \
		else  bin/python bootstrap.py; fi

buildoutcfg:
	@if test -f 'buildout.cfg'; \
		then echo "There is a buildout.cfg"; \
		else ln -s dev.cfg buildout.cfg; fi

start:
	$(bin/instance)

install: venv buildoutcfg bootstrap
	$(bin/buildout)

test: install
	bin/test

clean:
	rm -rf include bin parts lib develop-eggs
	rm -f .buildout.cfg .installed.cfg .mr.developer.cfg bootstrap.py
	docker-compose rm --force
build:
	export USERID=$(shell id -u -r) && \
	export GROUPID=$(shell id -g -r) && \
	cat Dockerfile.tmpl | envsubst > Dockerfile
	docker build -t $(IMAGE) .
	docker run --name indexing $(IMAGE) bash
	docker cp indexing:/code/devel .
	docker rm indexing
up:
	docker-compose run --service-ports web
run: up
test:
	docker-compose run web /code/bin/test
