# Use a lightweight Nginx image to serve static content
FROM nginx:alpine


# Expose port 80
EXPOSE 80


COPY data/* /usr/share/nginx/html/data/
COPY html/* /usr/share/nginx/html/
COPY css/* /usr/share/nginx/html/css/
COPY js/* /usr/share/nginx/html/js/
COPY partials/* /usr/share/nginx/html/partials/

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]