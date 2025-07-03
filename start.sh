#!/bin/bash

# Tusky Bot Startup Script for Pterodactyl Panel
# This script handles the installation and startup of the Tusky bot

echo "=== Tusky Bot Startup Script ==="
echo "Starting at: $(date)"

# Set environment variables
export NODE_ENV=production
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=false
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# Install system dependencies if needed (for Pterodactyl with root access)
if command -v apt-get &> /dev/null; then
    echo "Installing system dependencies..."
    apt-get update -qq
    apt-get install -y chromium-browser fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libdrm2 libgtk-3-0 libnspr4 libnss3 libxss1 libxtst6 xdg-utils
fi

# Create downloads directory
mkdir -p downloads

# Install npm dependencies
echo "Installing npm dependencies..."
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found"
    exit 1
fi

# Clean install
rm -rf node_modules package-lock.json
npm install --production

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Error: npm install failed"
    exit 1
fi

# Verify puppeteer installation
echo "Verifying Puppeteer installation..."
node -e "
try {
    const puppeteer = require('puppeteer');
    console.log('Puppeteer version:', require('puppeteer/package.json').version);
    console.log('Puppeteer installed successfully');
} catch (error) {
    console.error('Puppeteer installation failed:', error.message);
    process.exit(1);
}
"

# Check if main file exists
if [ ! -f "index.js" ]; then
    echo "Error: index.js not found"
    exit 1
fi

# Set proper permissions
chmod +x index.js

# Start the bot
echo "Starting Tusky Bot..."
echo "=== Bot Logs ==="

# Run with proper error handling
