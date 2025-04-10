#!/bin/bash

# Create .profile and set binaries path
touch $HOME/.profile

echo 'PATH=/QOpenSys/pkgs/bin:$PATH' >> $HOME/.profile
echo 'export PATH' >> $HOME/.profile

# Install system dependencies
yum install -y git \
    python39-pip \
    python39-devel \
    python39-paramiko \
    python39-cryptography \
    python39-numpy \
    python39-pynacl \
    python39-bcrypt \
    python39-lxml

# Install pip dependenices
pip3.9 install bs4 \
    beautifulsoup4 \
    urllib3 \
    configobj \
    requests \
    certifi \
    Jinja2 \
    scp

# Install schily to generate cloudinit
yum-config-manager --add-repo http://www.the-i-doctor.com/oss/repo/the-i-doctor.repo
yum install -y schily-tools
echo 'export PATH=$PATH:/opt/schily/bin' >> $HOME/.profile

mkdir -p source
cd source

# Clone source code from github repo
git clone --branch v0.0.1 git@github.ibm.com:project-pim/pim.git
cd pim
