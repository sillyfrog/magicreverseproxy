#!/bin/sh

certbot renew --webroot --webroot-path /usr/share/nginx/html --post-hook 'nginx -s reload'
