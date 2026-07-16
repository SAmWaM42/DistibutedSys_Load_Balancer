#!/bin/bash
set -e
if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed."
    exit 1
fi

cd Server
if docker image inspect default_server >/dev/null 2>&1; then
    echo "Image already exists"
    
else
    docker build -t default_server .
    echo "server image built created  ..........."
fi

cd ..
cd Balancer

if docker image inspect load_balancer >/dev/null 2>&1; then
    echo "Image already exists"
else
    docker build -t load_balancer .
    echo "load balancer image built created  ..........."
fi

if ! docker network inspect net1 >/dev/null 2>&1; then
    docker network create net1
    echo "docker network created  ..........."
fi

if docker container inspect balancer_1 >/dev/null 2>&1; then
    echo "Balancer already exists:Using exsisting container"
else
    docker run --privileged -d --name balancer_1 -p 8080:5000 --network net1 -v /var/run/docker.sock:/var/run/docker.sock load_balancer
    echo "balancer created ..........."
fi


cd ..
cd Client

python3 -m pip install --no-cache-dir -r requirements.txt
python3 request.py




