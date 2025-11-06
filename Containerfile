FROM fedora:43

# Install Python and pip
RUN dnf install -y procps-ng python3 python3-pip python3-wheel && \
    dnf clean all

# Install CarConnectivity packages to system path
RUN pip3 install --no-cache-dir --prefix=/usr/local 'carconnectivity[all]' carconnectivity-plugin-database

# Ensure pip installed binaries are in PATH
ENV PATH="/usr/local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Expose CarConnectivity webserver port
EXPOSE 4000

# Run CarConnectivity CLI with config
CMD ["carconnectivity", "/app/config/carconnectivity_config.json"]
