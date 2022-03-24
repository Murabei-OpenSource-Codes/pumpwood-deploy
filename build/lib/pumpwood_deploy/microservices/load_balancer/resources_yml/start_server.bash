#!/usr/bin/env bash
echo "Configuring Gateway"
sed -i "s/{{TARGET_SERVICE}}/${TARGET_SERVICE}/g;" /etc/nginx/conf.d/proxy_server.conf
sed -i "s/{{SERVER_NAME}}/${SERVER_NAME}/g;" /etc/nginx/conf.d/proxy_server.conf

echo "Starting nginx..."
nginx -g 'daemon off;'
