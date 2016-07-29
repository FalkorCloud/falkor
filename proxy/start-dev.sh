#!/usr/bin/env bash

exec sudo docker run --rm -it \
  --name my-app-dev --net=host \
  -v "$(pwd)/nginx/conf":/opt/openresty/nginx/conf \
  -v "$(pwd)/nginx/lualib":/opt/openresty/nginx/lualib \
  -p 9090:8080 \
  ficusio/openresty:debian "$@"
