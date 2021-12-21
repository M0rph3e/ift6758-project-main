#!/bin/bash

echo "Running..."

docker run -it -e 127.0.0.1:5000:5000/tcp --env COMET_API_KEY=$COMET_API_KEY ift6758/serving:$1
#echo $COMET_API_KEY