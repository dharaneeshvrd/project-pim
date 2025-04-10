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
    python39-lxml \
    python3-jinja2

# Install pip dependenices
pip3.9 install bs4 \
    beautifulsoup4 \
    urllib3 \
    configobj \
    requests \
    certifi

# Install schily to generate cloudinit
yum-config-manager --add-repo http://www.the-i-doctor.com/oss/repo/the-i-doctor.repo
yum install -y schily-tools 
export PATH=$PATH:/opt/schily/bin

mkdir -p pim
cd pim

# Download source code tarball from github repo
wget -O pim.tar.gz https://codeload.github.ibm.com/project-pim/pim/tar.gz/refs/tags/v0.0.1?token=AADUNXZM5FKJWT4BUZIBOQLH6TUBM
tar xf pim.tar.gz
rm pim.tar.gz
cd pim-0.0.1
