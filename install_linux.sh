#!/bin/bash

dnf install -y python3-pip libxml2-devel libxslt-devel rust cargo python-devel libffi-devel
dnf groupinstall -y "Development Tools"
pip install uv

# Clone source code from github repo
git clone git@github.ibm.com:project-pim/pim.git
cd pim
export PYTHONPATH=.

uv venv
source .venv/bin/activate
uv sync
