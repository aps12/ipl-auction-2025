#!/bin/bash

# Set up writable directories
INSTALL_DIR="$HOME/chrome"
CHROMEDRIVER_DIR="$HOME/chromedriver"

# Create directories if not exist
mkdir -p "$INSTALL_DIR"
mkdir -p "$CHROMEDRIVER_DIR"

echo "✅ Downloading Google Chrome..."
curl -o /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

echo "✅ Extracting Google Chrome..."
dpkg -x /tmp/google-chrome.deb "$INSTALL_DIR"

# Set Chrome path
CHROME_BINARY="$INSTALL_DIR/opt/google/chrome/google-chrome"

echo "✅ Downloading ChromeDriver..."
CHROME_VERSION=$("$CHROME_BINARY" --version | awk '{print $3}')
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip"

curl -o /tmp/chromedriver.zip "$CHROMEDRIVER_URL"

echo "✅ Extracting ChromeDriver..."
unzip /tmp/chromedriver.zip -d "$CHROMEDRIVER_DIR"
chmod +x "$CHROMEDRIVER_DIR/chromedriver"

# Set environment variables
export PATH="$CHROMEDRIVER_DIR:$PATH"
export CHROME_BIN="$CHROME_BINARY"

echo "✅ Chrome and ChromeDriver setup completed!"
echo "🔹 Chrome Path: $CHROME_BINARY"
echo "🔹 ChromeDriver Path: $CHROMEDRIVER_DIR/chromedriver"

# Verify installation
"$CHROME_BINARY" --version
"$CHROMEDRIVER_DIR/chromedriver" --version
