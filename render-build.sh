#!/usr/bin/env bash
set -e

# Install dependencies for Chrome
sudo apt-get update
sudo apt-get install -y \
    wget \
    unzip \
    xvfb \
    libgconf-2-4

# Install Chrome Browser
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f 3 | cut -d '.' -f 1)
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)
wget -q https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip -q chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

echo "Chrome and ChromeDriver installed successfully!"