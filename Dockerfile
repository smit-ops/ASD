
FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html

COPY images /usr/share/nginx/html/images

COPY real_fruits /usr/share/nginx/html/real_fruits

COPY static /usr/share/nginx/html/static

COPY icons /usr/share/nginx/html/icons

COPY Tutorials /usr/share/nginx/html/Tutorials

EXPOSE 80
