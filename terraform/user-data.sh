#!/bin/bash

set -ex
sudo apt-get update -y
sudo apt-get install -y \
    docker.io \
    docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
mkdir -p /home/ubuntu/app
chown ubuntu:ubuntu /home/ubuntu/app
