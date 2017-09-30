SHELL := /bin/bash
CWD := $(shell pwd)
IMAGE := "jamrizzi/volback-agent:latest"
SOME_CONTAINER := $(shell echo some-$(IMAGE) | sed 's/[^a-zA-Z0-9]//g')
DOCKERFILE := $(CWD)/Dockerfile

.PHONY: all
all: clean deps build

.PHONY: start
start: env
	@python ./app/ --help

.PHONY: build
build:
	@echo Building: $(IMAGE)
	@docker build -t $(IMAGE) -f $(DOCKERFILE) $(CWD)
	@echo ::: Built :::

.PHONY: test
test: env
	@docker run --name some-python --rm -v $(CWD):/app python:2.7 /app/env/bin/python /app/tests
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
	@docker pull $(IMAGE)
	@echo ::: Pulled :::

.PHONY: push
push:
	@docker push $(IMAGE)
	@echo ::: Pushed :::

.PHONY: run
run:
	@echo Running: $(IMAGE)
	@docker run --name $(SOME_CONTAINER) --rm $(IMAGE) -h

.PHONY: ssh
ssh:
	@dockssh $(IMAGE)

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
