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
Configure domain, Github key and secret
```
cp hub/falkor_project/config_sample.py hub/falkor_project/config.py 
edit hub/falkor_project/config.py 
```
Start everything
```
DOMAIN_NAME="localhost.be" docker-compose up
```
Or in development
```
DOMAIN_NAME="us2.peragro.org" docker-compose up --build --force-recreate
```
Share the docker socket with the web container
```
web_ip=$(docker inspect --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" falkor_web_1)
sudo socat -d -d TCP-L:2375,fork,range=$web_ip/32 UNIX:/var/run/docker.sock
```
Setup the db
```
docker exec -it falkor_web_1 python manage.py migrate
``` 
Login with Github and make your own user the superuser
```
docker exec -it falkor_web_1 python manage.py shell
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

```