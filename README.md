# PIM Linux Sidecar for wrapping bootable AI workloads

## Pre-requisites
1. Hardware host to create logical partition, VIOS to attach physical volume and virtual optical devices
2. bootstrap ISO(ppc64le) and cloud-init ISO
3. IBMi partition to run the PIM automation script

## Dependencies
All dependencies are captured in requirements.txt
1. python requests module for REST communication
2. paramiko and scp modules for performing scp operation
3. bs4 (beautifulsoup) and lxml modules for XML parsing

## Install depenencies on IBMi partition

1. Currently the source code for PIM is internal, needs to be cloned by adding SSH key of the IBMi partition
2. Run Installer script to install system and python dependencies needed for running PIM

```
bash install.sh
```

## Key in all the PIM configurations related to lpar, AI workload, etc in `config.ini`

## Run PIM lifecycle manager

  ```
  export PYTHONPATH=.
  export PATH=$PATH:/opt/schily/bin
  python3 cmd/pim.py [launch/destroy]
  ```

