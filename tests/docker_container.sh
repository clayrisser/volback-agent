docker run -d --rm --name some-mongo -v /data/some-mongo/:/data/db mongo:latest 1>/dev/null
docker run -d --rm --name some-alpine -v /data/some-alpine1/:/data1 -v /data/some-alpine2/:/data2 alpine:latest tail -f /dev/null
mkdir -p /data/some-alpine1 && echo world > /data/some-alpine1/hello
mkdir -p /data/some-alpine2 && echo hello > /data/some-alpine2/world
docker ps
docker run --name some-python --rm -e PYTHONPATH=/app/ -v /app/:/app/ -v /var/run/docker.sock:/var/run/docker.sock jamrizzi/volback-agent:test \
       /bin/sh /app/tests/test_container.sh
docker stop $(docker ps -aq) 1>/dev/null
