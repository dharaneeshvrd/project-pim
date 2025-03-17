# PIM Linux Sidecar for wrapping bootable AI workloads

## Pre-requisites
1. Hardware host to create logical partition and deploy PIM linux sidecar
2. Custom ISO(ppc64le) with cloud-init

## Dependencies
All dependencies are captured in requirements.txt
1. python requests module for REST communication
2. paramiko and scp modules for performing scp operation
3. bs4 (beautifulsoup) and lxml modules for XML parsing

## Install depenencies in python virtual environment

```
python3 -m venv myvirtual_venv
source myvirtual_venv/bin/activate
pip3 install -r requirements.txt
```
### NOTE: If there are rust related errors during installation of dependencies, install cargo additionally
          ** If there are cryptography related errors,  install python-dev libxml2-dev libxslt-dev packages **

## Modify HMC, VIOS, partition related configurations in `config.ini`

## Run PIM lifecycle manager

  ```
  export PYTHONPATH=.
  python3 cmd/pim.py [launch/destroy]
  ```
  