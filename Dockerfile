FROM python:3.6

COPY . /code
WORKDIR /code

ENTRYPOINT ["/code/docker-entrypoint.sh"]
