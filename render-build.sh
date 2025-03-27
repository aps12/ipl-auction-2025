#!/usr/bin/env bash

# Download and install a portable version of Google Chrome
mkdir -p ~/chrome
wget -O ~/chrome/chrome-linux.zip https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
unzip ~/chrome/chrome-linux.zip -d ~/chrome/
chmod +x ~/chrome/chrome

# Download and install ChromeDriver
CHROME_VERSION=$(~/chrome/chrome --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O ~/chrome/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip ~/chrome/chromedriver.zip -d ~/chrome/
chmod +x ~/chrome/chromedriver

echo "✅ Google Chrome & ChromeDriver Installed Successfully!"
