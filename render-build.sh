#!/usr/bin/env bash

# Install Google Chrome (without sudo)
wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt update && apt install -y ./google-chrome.deb
rm google-chrome.deb

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -N https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

echo "✅ Google Chrome & ChromeDriver Installed Successfully!"
