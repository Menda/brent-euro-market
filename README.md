Brent Euro Market
=================

This project is a personal project used to develop personal skills on:

* Design patterns
* Monitoring
* Caching
* asyncio
* Binary search
* Queues: RabbitMQ
* Cassandra database


Installation and run
====================

Docker must be installed in order to run it.

```bash
docker-compose -f docker-compose.yml build
```

To run the application

```bash
docker-compose -f docker-compose.yml up
```


Management and development
==========================

Bash inside a new container:

```bash
docker-compose -f docker-compose.yml run --entrypoint '/usr/bin/env' --rm brent_euro_market bash
```

To run the application with pdb support:

```bash
docker-compose -f docker-compose.yml run --service-ports --rm brent_euro_market
```

To run the tests:

```bash
docker-compose -f docker-compose.yml run --entrypoint 'python -m unittest discover .' --rm brent_euro_market
```
