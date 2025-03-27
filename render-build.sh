#!/usr/bin/env bash
set -e  # Exit immediately if a command exits with a non-zero status

# Set up directories
INSTALL_DIR="/tmp/chrome"
mkdir -p "$INSTALL_DIR"

# Download Chrome .deb package
wget -q -O "$INSTALL_DIR/google-chrome.deb" "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"

# Extract Chrome without installing system-wide
cd "$INSTALL_DIR"
ar x google-chrome.deb
tar -xf data.tar.xz

# Find Chrome binary
CHROME_BINARY=$(find "$INSTALL_DIR" -path "*/google-chrome" | head -n 1)
if [ -z "$CHROME_BINARY" ]; then
    echo "❌ Google Chrome binary not found!"
    exit 1
fi
chmod +x "$CHROME_BINARY"

# Get Chrome version
CHROME_VERSION=$("$CHROME_BINARY" --version | awk '{print $3}' | cut -d'.' -f1)

# Fetch compatible ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# Download ChromeDriver
wget -q -O "$INSTALL_DIR/chromedriver.zip" "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

# Unzip ChromeDriver
unzip -q -o "$INSTALL_DIR/chromedriver.zip" -d "$INSTALL_DIR/"

# Find ChromeDriver binary
CHROMEDRIVER_BINARY=$(find "$INSTALL_DIR" -name "chromedriver" | head -n 1)
if [ -z "$CHROMEDRIVER_BINARY" ]; then
    echo "❌ ChromeDriver binary not found!"
    exit 1
fi
chmod +x "$CHROMEDRIVER_BINARY"

# Create a list of paths for Python script to check
echo "$CHROME_BINARY" > /tmp/chrome_binary_path
echo "$CHROMEDRIVER_BINARY" > /tmp/chromedriver_binary_path

echo "✅ Google Chrome & ChromeDriver Extracted Successfully!"
echo "Chrome Binary: $CHROME_BINARY"
echo "ChromeDriver Binary: $CHROMEDRIVER_BINARY"