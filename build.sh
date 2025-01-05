#!/bin/bash

# Update system package list
apt-get update

# Install TeX Live
apt-get install -y texlive-full

# Install additional tools for LaTeX to image conversion
apt-get install -y poppler-utils
