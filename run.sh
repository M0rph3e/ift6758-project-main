#!/bin/bash

echo "Running..."

docker run -it --expose 127.0.0.1:5000:5000/tcp --env DOCKER_ENV_VAR=$COMET_API_KEY ift6758/serving:1.0.0
echo $COMET_API_KEY