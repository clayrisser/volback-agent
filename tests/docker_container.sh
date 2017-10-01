docker run -d --rm --name some-mongo -v /data/some-mongo/:/data/db mongo:latest 1>/dev/null
docker run --name some-python --rm -e PYTHONPATH=/app/ -v /app/:/app/ -v /var/run/docker.sock:/var/run/docker.sock jamrizzi/volback-agent:test \
       /bin/sh /app/tests/test_container.sh
docker stop $(docker ps -aq) 1>/dev/null
