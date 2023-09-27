FROM redis:latest
LABEL authors="pgalandev"
# Expose port 6379
EXPOSE 6379

# Copy the init-redis.sh script into the container
COPY init-redis.sh /usr/local/bin/

# Make the script executable
RUN chmod +x /usr/local/bin/init-redis.sh

ENTRYPOINT ["/usr/local/bin/redis-server"]
