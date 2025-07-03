# Dockerfile for Tusky Bot (Alternative setup)
FROM node:18-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome path
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy source code
COPY . .

# Create downloads directory
RUN mkdir -p downloads

# Set proper permissions
RUN chmod +x start.sh

# Expose port (if needed)
EXPOSE 3000

# Start the application
CMD ["./start.sh"]
