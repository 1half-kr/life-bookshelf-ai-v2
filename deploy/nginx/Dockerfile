# Use official nginx alpine image for minimal size
FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf \
    && rm /etc/nginx/nginx.conf

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Create log directory with proper permissions
RUN mkdir -p /var/log/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chmod -R 755 /var/log/nginx

# Create cache directory for nginx
RUN mkdir -p /var/cache/nginx \
    && chown -R nginx:nginx /var/cache/nginx

# Create run directory for PID file
RUN mkdir -p /var/run \
    && chown -R nginx:nginx /var/run \
    && chmod -R 755 /var/run

# Add health check script
RUN echo '#!/bin/sh' > /usr/local/bin/health-check.sh \
    && echo 'curl -f http://localhost/health || exit 1' >> /usr/local/bin/health-check.sh \
    && chmod +x /usr/local/bin/health-check.sh

# Install curl for health checks
RUN apk add --no-cache curl

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Expose port 80
EXPOSE 80

# Start nginx in foreground (root 권한으로 시작하되 worker는 nginx 사용자로)
CMD ["nginx", "-g", "daemon off;"]
