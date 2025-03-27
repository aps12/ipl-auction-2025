#!/bin/bash

set -e  # Exit on first error

echo "✅ Downloading Google Chrome..."
wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

echo "✅ Extracting Google Chrome..."
mkdir -p /tmp/chrome
dpkg-deb -x /tmp/google-chrome.deb /tmp/chrome/

echo "✅ Checking Chrome version..."
CHROME_VERSION=$(/tmp/chrome/opt/google/chrome/google-chrome --version | awk '{print $3}')
echo "🔹 Installed Chrome version: $CHROME_VERSION"

echo "✅ Finding closest compatible ChromeDriver version..."
LATEST_CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)

echo "✅ Downloading ChromeDriver $LATEST_CHROMEDRIVER_VERSION..."
wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

echo "✅ Extracting ChromeDriver..."
mkdir -p /tmp/chromedriver
unzip /tmp/chromedriver.zip -d /tmp/chromedriver/
chmod +x /tmp/chromedriver/chromedriver

echo "✅ Chrome and ChromeDriver setup completed!"
echo "🔹 Chrome Path: /tmp/chrome/opt/google/chrome/google-chrome"
echo "🔹 ChromeDriver Path: /tmp/chromedriver/chromedriver"

# Export paths for Selenium
export PATH=$PATH:/tmp/chrome/opt/google/chrome
export PATH=$PATH:/tmp/chromedriver