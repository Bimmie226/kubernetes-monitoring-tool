FROM nginx:1.27-alpine

ENV NGINX_ENVSUBST_OUTPUT_DIR=/usr/share/nginx/html

COPY index.html monitoring.html /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/
COPY config.txt.template /etc/nginx/templates/config.txt.template

EXPOSE 80
