Falkor
====
Soar through the cloud

Cloud9 hub

Installation
-----
Set up a domain if you don't have one
```
sudo apt-get install dnsmasq
sudo nano /etc/dnsmasq.conf
add 'address=/localhost.be/192.168.1.3'
```
Get a certificate
```
docker run -it --rm -p 443:443 -p 80:80 --name certbot \
            -v "/etc/letsencrypt:/etc/letsencrypt" \
            -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
            quay.io/letsencrypt/letsencrypt:latest certonly
```           
Configure domain, Github key and secret
```
cp hub/falkor_project/config_sample.py hub/falkor_project/config.py 
edit hub/falkor_project/config.py 
```
Start everything
```
DOMAIN_NAME="localhost.be"  SECRET="somesecret" docker-compose up
```
Or in development
```
DOMAIN_NAME="us2.peragro.org"  SECRET="somesecret" docker-compose up --build --force-recreate
```
Setup the db
```
docker-compose exec web-worker python manage.py migrate
``` 
Login with Github and make your own user the superuser
```
docker-compose exec web-worker python manage.py shell
>>> from django.contrib.auth.models import User
>>> u = User.objects.all()[0]
>>> u.is_superuser = True
>>> u.is_staff=True
>>> u.save()
```


Running
-------

Create a workspace and open it, in the terminal run:
``` 
python -m SimpleHTTPServer
``` 
Falkor will list this endpoint.


Development
------------
``` 
find . -type f -iname '*.py' | entr /bin/sh -c 'docker-compose build dockerworker && docker-compose up -d  --no-deps dockerworker'
find . -type f -iname '*.py' | entr /bin/sh -c 'docker-compose build web-worker && docker-compose up -d --no-deps web-worker && docker-compose exec web-worker python manage.py migrate'
``` 

 
Scrap
------
``` 
#Expose the container to host
socat TCP-LISTEN:8000,fork TCP:172.17.0.7:8000
 

docker run -it -d -v /tmp/mux:/tmp -p 9002:80 kdelfour/cloud9-docker
docker run -it --rm --volumes-from 444 -v /tmp/mux:/tmp tmux /bin/bash


volumeId=$(sudo docker create -v /tmp -v /workspace -v /root/.c9 -v /cloud9 --name shared cloud9 /bin/true)
sudo docker run -it -d  --volumes-from $volumeId tmux /bin/bash -c 'rm -R /tmp/tmux-0; tmux -L cloud91.9'
sudo docker run -it -d -p 9002:80 --volumes-from $volumeId cloud9

unison . ssh://sueastside@us2.peragro.org//home/sueastside/Projects/cloud39 -auto -batch -repeat 3 -force .



docker start $(docker ps -a | grep falkor__user_ | awk "{print \$2}")
 
sudo docker volume ls -q | xargs -l1 docker volume inspect --format '{{ .Mountpoint }}' |  xargs -t -l1 sudo ls

docker ps -a | grep falkor__user_ | awk "{print \$2}" | xargs -l1 -I conname -t docker exec conname find /workspace -type f ! -wholename '*.c9*' -exec du -sh {} \;



https://gist.githubusercontent.com/Stiveknx/8f574fc20addc74bef80/raw/2f20d9fe00d1331f5fe1053eda71dc9910f57f80/nginx.conf
https://github.com/c9/core/blob/master/plugins/c9.vfs.standalone/standalone.js#L51
https://github.com/c9/core/issues/237#issuecomment-175899228

npm config get production
npm config set -g production false


https://github.com/scrooloose/vimfiles


tail -f /var/log/something to keep it running
```