docker run -d --rm --name some-mongo mongo:latest 1>/dev/null
docker run --name some-python --rm -e PYTHONPATH=/app/ -v /app/:/app/ -v /var/run/docker.sock:/var/run/docker.sock python:2.7 \
       /app/env/bin/python /app/tests
docker stop $(docker ps -aq) 1>/dev/null
