# Docker Compose Lab

This lab is intended to give you practical experience in the following things:

* Writing and updating your own Docker Compose file.
* Using Docker Compose to discover running ports.
* Utilizing networks to ensure application isolation (and simplify config).
* Debugging container failures.

## Introduction

This lab uses git tags, to "jump ahead" in time. Before you get started, make sure you checkout the tag for `1-in-memory-implementation`.

```
$ git checkout 1-in-memory-implementation
```

This lab also assumes you're using the docker-toolbox for MacOS (and are therefore using a Docker machine).


## Part 1: Introducing the Value Microservice.

The [app](app/) directory of this repo contains a tiny Dockerized Python microservice that we'll call the "value" service for now. It has a single endpoint, `/value`, with the following API.
* `GET /value` returns a JSON object with the key `value` set to the current value (a string).
* `POST /value` will set the current `value`.

It's a dumb microservice, and it's really only here to serve our Docker Compose system.  

To run the service, do the following.

```
$ docker-compose build
$ docker-compose up
```

You'll see the following messages once the microservice is online:

```
Recreating dockercomposelab_webservice_1 ...
Recreating dockercomposelab_webservice_1 ... done
Attaching to dockercomposelab_webservice_1
webservice_1  | Bottle v0.12.13 server starting up (using WSGIRefServer())...
webservice_1  | Listening on http://0.0.0.0:8080/
webservice_1  | Hit Ctrl-C to quit.
```

Sweet! However, the message is a little misleading. 

```
$ curl http://0.0.0.0:8080/
curl: (7) Failed to connect to 0.0.0.0 port 8080: Connection refused
```

What a tease. It turns out that the `0.0.0.0` refers to the container's network interface, not our computer's network interface.

We can see this pretty clearly if we use the `docker ps` command, and look at the `PORTS` column.


```
$ docker ps
CONTAINER ID        IMAGE                         COMMAND             CREATED             STATUS              PORTS                     NAMES
d32d5f6c0640        dockercomposelab_webservice   "python app.py"     27 minutes ago      Up 27 minutes       0.0.0.0:32768->8080/tcp   dockercomposelab_webservice_1
```

We can get just the mapping with the `docker-compose port` command. The following lets us find out which port has bound to port 8080 on the `webservice` service. 

```
$ docker-compose port webservice 8080
0.0.0.0:32768
```

Aha! So it must be on `0.0.0.0:32768`. Not so fast.

```
$ curl http://0.0.0.0:32768/
curl: (7) Failed to connect to 0.0.0.0 port 32768: Connection refused 
```

It turns out that the `0.0.0.0` in the Docker commands refers to the Docker machine, a VirtualBox VM that is running on your computer. You can get the IP address for that machine using the `docker-machine ip` command.

```
$ docker-machine ip
192.168.99.100
```

So, using the port and IP address together, I can talk to the service.


```
$ curl http://192.168.99.100:32768/value
{"value": "None"}
$ curl -X POST http://192.168.99.100:32768/value -H "Content-Type: application/json" -d '{"value": "potato"}'
$ curl http://192.168.99.100:32768/value
{"value": "potato"}
```

We've proven what we need to, so go ahead and tear down the Docker compose environment. Hit `CTRL + C` to exit.

Alright! Let's complicate our lives a little bit! Move on to the next tag.

```
$ git checkout 2-adding-redis-container
```

## Part 2: Debugging Failed Containers

Let's relaunch the environment, using the detached mode (`-d` flag). 

```
$ docker compose up -d
Creating network "dockercomposelab_default" with the default driver
Creating dockercomposelab_webservice_1 ...
Creating dockercomposelab_webservice_1 ... done
```

But there's an issue. Let's try and find the running containers.

```
$ docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
```

Huh. It looks like our container already died. We can ask `docker ps` to show us stopped containers.

```
$ docker ps --filter status=exited
CONTAINER ID        IMAGE                         COMMAND             CREATED             STATUS                     PORTS               NAMES
5d85bafe5fde        dockercomposelab_webservice   "python app.py"     6 minutes ago       Exited (1) 6 minutes ago                       dockercomposelab_webservice_1
```

Now, we can fetch the logs for that container.

```
$ docker logs 5d85bafe5fde
Traceback (most recent call last):
  File "app.py", line 29, in <module>
    redis_url = os.environ["REDIS_URL"]
  File "/usr/local/lib/python2.7/UserDict.py", line 40, in __getitem__
    raise KeyError(key)
KeyError: 'REDIS_URL'
```

Ah. So we need to set up a 

