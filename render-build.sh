#!/usr/bin/env bash

# Set up directories
INSTALL_DIR="/opt/render/chrome"
mkdir -p $INSTALL_DIR

# ✅ Download the latest stable Google Chrome binary
wget -O $INSTALL_DIR/google-chrome.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"

# ✅ Install Google Chrome
dpkg -x $INSTALL_DIR/google-chrome.deb $INSTALL_DIR/ || {
    echo "❌ Failed to extract Google Chrome!"
    exit 1
}

# ✅ Find the Chrome binary
CHROME_BINARY=$(find $INSTALL_DIR -name "google-chrome-stable" | head -n 1)
if [ -z "$CHROME_BINARY" ]; then
    echo "❌ Google Chrome binary not found!"
    exit 1
fi
chmod +x "$CHROME_BINARY"

# ✅ Get Chrome version and install compatible ChromeDriver
CHROME_VERSION=$("$CHROME_BINARY" --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

wget -O $INSTALL_DIR/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip -o $INSTALL_DIR/chromedriver.zip -d $INSTALL_DIR/

CHROMEDRIVER_BINARY=$(find $INSTALL_DIR -name "chromedriver" | head -n 1)
if [ -z "$CHROMEDRIVER_BINARY" ]; then
    echo "❌ ChromeDriver binary not found!"
    exit 1
fi
chmod +x "$CHROMEDRIVER_BINARY"

echo "✅ Google Chrome & ChromeDriver Installed Successfully!"
