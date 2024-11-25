BASEDIR=/home/sample-user/sample-container
docker run \
	-d \
	--restart always \
	--name mycontainer \
	-p 8081:8081 \
	-v /home/sample-user/samples:/samples \
	-v $BASEDIR/run:/tmp/sockets \
	-v $BASEDIR/logs:/tmp/log \
	myimage
