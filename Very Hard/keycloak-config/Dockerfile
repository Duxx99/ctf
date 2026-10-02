# Dockerfile for Keycloak
FROM quay.io/keycloak/keycloak:22.0.3

# Copy realm configuration
COPY realm-export.json /opt/keycloak/data/import/realm-export.json

# Expose the ports Keycloak will use
EXPOSE 8080

# Default command, overridden by docker-compose command if needed
CMD ["start-dev", "--import-realm"]
