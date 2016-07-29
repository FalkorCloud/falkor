#!/bin/sh

sed -i "s/localhost.be/${DOMAIN_NAME}/g" /opt/openresty/nginx/conf/nginx.conf

nginx -g "daemon off; error_log /dev/stderr info;"