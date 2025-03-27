#!/usr/bin/env bash
# Set up directories
INSTALL_DIR="/opt/render/chrome"
mkdir -p $INSTALL_DIR

# Download the latest stable Google Chrome binary
wget -q -O $INSTALL_DIR/google-chrome.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"

# Install Google Chrome
dpkg -x $INSTALL_DIR/google-chrome.deb $INSTALL_DIR/ || {
    echo "❌ Failed to extract Google Chrome!"
    exit 1
}

# Find the Chrome binary (updated search path)
CHROME_BINARY=$(find $INSTALL_DIR -path "*/google-chrome" | head -n 1)
if [ -z "$CHROME_BINARY" ]; then
    echo "❌ Google Chrome binary not found!"
    exit 1
}
chmod +x "$CHROME_BINARY"

# Get Chrome version
CHROME_VERSION=$("$CHROME_BINARY" --version | awk '{print $3}' | cut -d'.' -f1)

# More robust ChromeDriver version fetching
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")

# Download ChromeDriver
wget -q -O $INSTALL_DIR/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"

# Unzip ChromeDriver
unzip -q -o $INSTALL_DIR/chromedriver.zip -d $INSTALL_DIR/

# Find ChromeDriver binary
CHROMEDRIVER_BINARY=$(find $INSTALL_DIR -name "chromedriver" | head -n 1)
if [ -z "$CHROMEDRIVER_BINARY" ]; then
    echo "❌ ChromeDriver binary not found!"
    exit 1
}
chmod +x "$CHROMEDRIVER_BINARY"

echo "✅ Google Chrome & ChromeDriver Installed Successfully!"
echo "Chrome Binary: $CHROME_BINARY"
echo "ChromeDriver Binary: $CHROMEDRIVER_BINARY"