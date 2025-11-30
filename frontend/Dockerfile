# Use a lightweight Nginx image to serve static content
FROM nginx:alpine


# Expose port 80
EXPOSE 80


COPY data/* /usr/share/nginx/html/data/
COPY html/* /usr/share/nginx/html/

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]