#!/bin/bash

set -o allexport; source .env; set +o allexport

projectname=$1 #'movielist'
containername=$2 #'teamsdjango2019_movielist_1'

mkdir ./$projectname

ssh -t $SSH_CONNEXION "mkdir -p $SRV_WORK_DIR;
docker export $containername | gzip > $SRV_WORK_DIR/container_export.gz;
docker run --rm --volumes-from $containername -v $SRV_WORK_DIR:/backup ubuntu tar cvf /backup/volume_backup.tar /var/www/;
mysqldump -P3306 -h 127.0.0.1 -u root -p$MYSQL_ROOT_PASSWORD $projectname > $SRV_WORK_DIR/db_mysql.sql;
docker exec -e PGPASSWORD=$POSTGRES_ROOT_PASSWORD postgres pg_dump -U postgres $projectname > $SRV_WORK_DIR/db_postgres.sql;
docker inspect $containername > $SRV_WORK_DIR/dockerinspect.txt;
docker stop $containername;
docker rm $containername -v;
"

echo "Container name: $containername, Database name: $containername, Export date: $(date '+%Y-%m-%d')" > ./$projectname/info.txt

scp -r -p $SSH_CONNEXION:$SRV_WORK_DIR ./$projectname
scp -r -p $SSH_CONNEXION:$SRV_COMPOSE_DIR/$projectname'-compose.yml' ./$projectname

ssh -t $SSH_CONNEXION "rm -rf $SRV_WORK_DIR"
