SHELL := /bin/bash
CWD := $(shell pwd)
IMAGE := "jamrizzi/volback-agent"
TAG := "latest"
SOME_CONTAINER := $(shell echo some-$(IMAGE) | sed 's/[^a-zA-Z0-9]//g')
DOCKERFILE := $(CWD)/Dockerfile

.PHONY: all
all: clean deps build

.PHONY: start
start: env
	@python ./app/ --help

.PHONY: build
build:
	@echo Building: $(IMAGE):$(TAG)
	@docker build -t $(IMAGE):$(TAG) -f $(DOCKERFILE) $(CWD)
	@echo ::: Built :::

.PHONY: test
test: env
	-@docker rm -f some-docker &>/dev/null || true
	@echo starting tests . . .
	@docker run -d --name some-docker --privileged --rm -v $(CWD):/app/ -v /var/lib/dind:/var/lib/docker docker:dind 1>/dev/null
	@docker exec some-docker /bin/sh /app/tests/docker_container.sh
	@docker stop some-docker 1>/dev/null
	@echo ::: Test :::

.PHONY: publish
publish: dist
	@twine upload dist/*
	@echo ::: Published :::

dist: env
	@echo Building: dist
	@python setup.py sdist
	@python setup.py bdist_wheel
	@echo ::: Distribution Ready :::

env:
	@echo Building: env
	@virtualenv env
	@env/bin/pip install -r ./requirements.txt
	@echo created virtualenv

.PHONY: pull
pull:
	@docker pull $(IMAGE):$(TAG)
	@echo ::: Pulled :::

.PHONY: push
push:
	@docker push $(IMAGE):$(TAG)
	@echo ::: Pushed :::

.PHONY: run
run:
	@echo Running: $(IMAGE):$(TAG)
	@docker run --name $(SOME_CONTAINER) --rm $(IMAGE):$(TAG) -h

.PHONY: ssh
ssh:
	@dockssh $(IMAGE):$(TAG)

.PHONY: essh
essh:
	@dockssh -e $(SOME_CONTAINER)

.PHONY: freeze
freeze:
	@env/bin/pip freeze > ./requirements.txt
	@echo ::: Requirements Frozen :::

.PHONY: clean
clean:
	-@rm -rf ./env ./dist ./build ./dotcli.egg-info ./*/*.pyc ./*/*/*.pyc &>/dev/null || true
	@echo ::: Cleaned :::

.PHONY: deps
deps: docker
	@echo ::: Fetched Deps :::
.PHONY: docker
docker:
ifeq ($(shell whereis docker), $(shell echo docker:))
	curl -L https://get.docker.com/ | bash
endif
