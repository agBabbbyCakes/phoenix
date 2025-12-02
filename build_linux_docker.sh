#!/bin/bash
# Build Linux standalone using Docker (works on any platform)

set -e

echo "============================================================"
echo "Building Phoenix Dashboard for Linux using Docker"
echo "============================================================"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Ensure downloads/linux directory exists
mkdir -p downloads/linux

# Build using Docker
echo "Building Linux executable in Docker container..."
docker build -f Dockerfile.linux-build -t phoenix-linux-builder .

# Create a temporary container to extract files
CONTAINER_ID=$(docker create phoenix-linux-builder)

# Extract the built files
echo "Extracting built files..."
docker cp ${CONTAINER_ID}:/app/downloads/linux/. downloads/linux/

# Clean up
docker rm ${CONTAINER_ID}

echo ""
echo "============================================================"
echo "Build complete!"
echo "============================================================"
echo ""
echo "Files created in downloads/linux/:"
ls -lh downloads/linux/
echo ""


