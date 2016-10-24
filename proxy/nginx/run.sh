#!/bin/sh

sed -i "s/localhost.be/${DOMAIN_NAME}/g" "${NGINX_PREFIX}/conf/nginx.conf"

/usr/local/openresty/bin/openresty -g "daemon off;"