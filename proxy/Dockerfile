FROM openresty/openresty:latest-alpine

ENV DOMAIN_NAME=localhost.be

ENV NGINX_PREFIX /usr/local/openresty/nginx

WORKDIR $NGINX_PREFIX/

RUN rm -rf conf/* html/*
COPY nginx $NGINX_PREFIX/

ENTRYPOINT ["./run.sh"]

EXPOSE 8080
