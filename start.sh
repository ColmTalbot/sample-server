#!/bin/bash
BASEDIR=/Users/colmtalbot/modules/sample-server

docker run \
	-d \
	--env-file prod.env \
	--restart always \
	--name gwsaamplefind-server \
	-p 8090:8080 \
	-v /Users/colmtalbot/LVK_DATA:/samples \
	-v $BASEDIR/run:/tmp/sockets \
	-v $BASEDIR/logs:/var/log \
	gwsamplefind-server
