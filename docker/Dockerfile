# AutoForge Builder - Minimal Docker image for C++ compilation and analysis
FROM ubuntu:22.04

# Install build tools and static analysis tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    cmake \
    make \
    cppcheck \
    python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
