#!/bin/bash

docker stop gwsamplefind-server
docker rm gwsamplefind-server
docker build -t gwsamplefind-server .
