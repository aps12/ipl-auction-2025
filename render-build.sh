#!/usr/bin/env bash

# Set up directories
INSTALL_DIR="/opt/render/chrome"
mkdir -p $INSTALL_DIR

# ✅ Download a working version of Google Chrome (precompiled binary)
wget -O $INSTALL_DIR/chrome-linux.zip "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_120.0.6099.71-1_amd64.deb"

# ✅ Extract Chrome
dpkg -x $INSTALL_DIR/chrome-linux.zip $INSTALL_DIR/ || {
    echo "❌ Failed to extract Google Chrome!"
    exit 1
}

# ✅ Set the correct path
CHROME_BINARY=$(find $INSTALL_DIR -name "google-chrome-stable" | head -n 1)
if [ -z "$CHROME_BINARY" ]; then
    echo "❌ Google Chrome binary not found!"
    exit 1
fi
chmod +x "$CHROME_BINARY"

# ✅ Download ChromeDriver (compatible version)
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
