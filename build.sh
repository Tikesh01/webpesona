#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies required for Pillow and other packages
apt-get update
apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    zlib1g-dev

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
