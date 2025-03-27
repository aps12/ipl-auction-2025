#!/usr/bin/env bash
set -e

# Create installation directory
CHROME_DIR="/tmp/chrome-installation"
mkdir -p "$CHROME_DIR"
cd "$CHROME_DIR"

# Download Chrome for Headless Environments
wget -q -O google-chrome-stable.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Extract Chrome without system installation
mkdir -p chrome
dpkg -x google-chrome-stable.deb chrome

# Find Chrome binary
CHROME_BINARY=$(find "$CHROME_DIR/chrome" -name "google-chrome" | head -n 1)
if [ -z "$CHROME_BINARY" ]; then
    echo "❌ Chrome binary not found!"
    exit 1
fi

# Get Chrome version
CHROME_VERSION=$("$CHROME_BINARY" --version | awk '{print $3}' | cut -d'.' -f1)

# Download compatible ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -q -O chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

# Unzip ChromeDriver
unzip -q chromedriver.zip

# Chmod binaries
chmod +x chromedriver
chmod +x "$CHROME_BINARY"

# Create path files for Python to reference
echo "$CHROME_BINARY" > /tmp/chrome_binary_path
echo "$CHROME_DIR/chromedriver" > /tmp/chromedriver_binary_path

echo "✅ Chrome and ChromeDriver installed successfully!"
echo "Chrome Binary: $CHROME_BINARY"
echo "ChromeDriver: $CHROME_DIR/chromedriver"