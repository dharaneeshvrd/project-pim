# ASE Linux Sidecar for wrapping bootable AI workloads

## Pre-requisites
1. Hardware host to create logical partition and deploy ASE linux sidecar
2. Custom ISO(ppc64le) with cloud-init

## Dependencies
1. Pip install python requests module for REST communication
2. Pip install paramiko and scp modules for performing scp operation
3. Pip install bs4 (beautifulsoup) and lxml modules for XML parsing

## NOTE: Modify HMC, VIOS, partition related configurations in `config.init`

## Run ASE lifecycle manager

  ```
  python3 ase_manager.py
  ```