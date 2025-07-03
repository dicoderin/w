#!/bin/bash

# Quick Installation Script for Tusky Bot
echo "=== Tusky Bot Installation Script ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running as root (for system dependencies)
if [[ $EUID -eq 0 ]]; then
   print_warning "Running as root - will install system dependencies"
   INSTALL_SYSTEM_DEPS=true
else
   print_info "Running as user - skipping system dependencies"
   INSTALL_SYSTEM_DEPS=false
fi

# Check Node.js installation
print_info "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
    
    # Check if version is >= 16
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -lt 16 ]; then
        print_error "Node.js version 16 or higher required"
        exit 1
    fi
else
    print_error "Node.js not found. Please install Node.js 16 or higher"
    exit 1
fi

# Check npm installation
print_info "Checking npm installation..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm found: $NPM_VERSION"
else
    print_error "npm not found"
    exit 1
fi

# Install system dependencies if running as root
if [ "$INSTALL_SYSTEM_DEPS" = true ]; then
    print_info "Installing system dependencies..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        print_info "Using apt-get package manager"
        apt-get update -qq
        apt-get install -y \
            chromium-browser \
            fonts-liberation \
            libappindicator3-1 \
            libasound2 \
            libatk-bridge2.0-0 \
            libdrm2 \
            libgtk-3-0 \
            libnspr4 \
            libnss3 \
            libxss1 \
            libxtst6 \
            xdg-utils \
            wget \
            ca-certificates
        
        if [ $? -eq 0 ]; then
            print_success "System dependencies installed"
        else
            print_error "Failed to install system dependencies"
            exit 1
        fi
    elif command -v yum &> /dev/null; then
        print_info "Using yum package manager"
        yum install -y chromium
        print_success "System dependencies installed"
    else
        print_warning "Unknown package manager - please install Chromium manually"
    fi
fi

# Create necessary directories
print_info "Creating directories..."
mkdir -p downloads logs
print_success "Directories created"

# Clean previous installation
print_info "Cleaning previous installation..."
rm -rf node_modules package-lock.json
print_success "Previous installation cleaned"

# Install npm dependencies
print_info "Installing npm dependencies..."
npm install --production

if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Verify Puppeteer installation
print_info "Verifying Puppeteer installation..."
node -e "
try {
    const puppeteer = require('puppeteer');
    console.log('Puppeteer version:', require('puppeteer/package.json').version);
    console.log('✓ Puppeteer installed successfully');
} catch (error) {
    console.error('✗ Puppeteer installation failed:', error.message);
    process.exit(1);
}
"

if [ $? -ne 0 ]; then
    print_error "Puppeteer verification failed"
    exit 1
fi

# Check if Chromium is available
print_info "Checking Chromium installation..."
if command -v chromium-browser &> /dev/null; then
    print_success "Chromium found: chromium-browser"
    export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
elif command -v chromium &> /dev/null; then
    print_success "Chromium found: chromium"
    export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
elif command -v google-chrome &> /dev/null; then
    print_success "Chrome found: google-chrome"
    export PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome
else
    print_warning "Chromium not found in PATH - Puppeteer will download it"
fi

# Set permissions
print_info "Setting permissions..."
chmod +x start.sh
chmod +x install.sh
print_success "Permissions set"

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
    print_warning "Please edit .env file with your API keys"
fi

# Test basic functionality
print_info "Testing basic functionality..."
timeout 10 node -e "
const puppeteer = require('puppeteer');
(async () => {
    try {
        const browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        await page.goto('https://example.com');
        await browser.close();
        console.log('✓ Basic functionality test passed');
    } catch (error) {
        console.error('✗ Basic functionality test failed:', error.message);
        process.exit(1);
    }
})();
"

if [ $? -eq 0 ]; then
    print_success "Basic functionality test passed"
else
    print_error "Basic functionality test failed"
    exit 1
fi

# Installation complete
echo ""
print_success "=== Installation Complete ==="
echo ""
print_info "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: ./start.sh"
echo "3. Or run: node index.js"
echo ""
print_info "For troubleshooting, see TROUBLESHOOTING.md"
echo ""

# Check if all required files exist
print_info "Checking required files..."
REQUIRED_FILES=("index.js" "package.json" "start.sh" ".env")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        exit 1
    fi
done

print_success "All required files found"
print_success "Installation completed successfully!"

# Display system info
echo ""
print_info "System Information:"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "OS: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "PWD: $(pwd)"
echo "Date: $(date)"
echo ""
