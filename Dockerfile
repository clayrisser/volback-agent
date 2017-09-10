############################################################
# Dockerfile to run jamrizzi/volback-agent
# Based on Alpine
############################################################

FROM alpine:3.5

MAINTAINER Jam Risser (jamrizzi)

WORKDIR /app/

ENV PYTHONPATH=/app

RUN apk add --no-cache \
        borgbackup \
        python \
        tini && \
    apk add --no-cache --virtual build-deps \
        build-base \
        py-pip \
        python-dev && \
    pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./ /app/
RUN apk del build-deps

ENTRYPOINT ["/sbin/tini", "--", "python", "/app/app"]
