#!/bin/bash

set -o allexport; source .env; set +o allexport


projectname=$1 #'caravel'
containername=$2 #'teamslaravel2020_caravel_1'
volumename=$3 #'teamslaravel2020_caravel'
localdir=$4 #'./caravel/saveproject'


scp -r -p ./$localdir $SSH_CONNEXION:$SRV_WORK_DIR

# Necessary only if specific configuration out of volume
# zcat $SRV_WORK_DIR/container_export.gz | docker import - $containername

ssh -t $SSH_CONNEXION "docker volume create $volumename;
docker run --rm -v $volumename:/var/www -v $SRV_WORK_DIR:/backup ubuntu bash -c 'cd / && tar xvf /backup/volume_backup.tar';
rm -rf $SRV_WORK_DIR
"

echo "Please start manually the docker with the docker-compose and apply mysql/postgres dumps if required."
