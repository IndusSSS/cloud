FROM nginx:alpine

# Install wget with proper SSL handling
RUN apk add --no-cache --update \
    wget \
    ca-certificates \
    && update-ca-certificates

# Copy nginx configuration
COPY conf.d/cloud.conf /etc/nginx/conf.d/default.conf
COPY conf.d/health.conf /etc/nginx/conf.d/health.conf

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 