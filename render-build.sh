#!/bin/bash

set -e  # Exit on first error

echo "✅ Downloading Google Chrome..."
wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

echo "✅ Installing Google Chrome..."
apt update && apt install -y /tmp/google-chrome.deb

echo "✅ Checking Chrome version..."
/usr/bin/google-chrome --version

echo "✅ Getting compatible ChromeDriver version..."
CHROME_VERSION=$(/usr/bin/google-chrome --version | awk '{print $3}')
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)

echo "✅ Downloading ChromeDriver $CHROMEDRIVER_VERSION..."
wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

echo "✅ Extracting ChromeDriver..."
unzip /tmp/chromedriver.zip -d /tmp/chromedriver/
chmod +x /tmp/chromedriver/chromedriver

echo "✅ Chrome and ChromeDriver setup completed!"
echo "🔹 Chrome Path: /usr/bin/google-chrome"
echo "🔹 ChromeDriver Path: /tmp/chromedriver/chromedriver"

# Export paths for Selenium
export PATH=$PATH:/usr/bin/google-chrome
export PATH=$PATH:/tmp/chromedriver
