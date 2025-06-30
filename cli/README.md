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

## Install dependencies on IBMi partition

1. Currently the source code for PIM is internal, needs to be cloned by adding SSH key of the IBMi partition
2. Add internal github's SSH key to known_hosts file on IBMi partition
```
ssh-keyscan github.ibm.com >> ~/.ssh/known_hosts
```

3. Run Installer script from a bash shell on IBMi SSH terminal session to install system and python dependencies needed for running PIM

```
bash install.sh
```

## PIM User Role
The user must have either the default role `hmcsuperadmin` or mandatory task roles listed below.

List of task roles required by user.
- Managed System
  - Create Partitions
  - View Managed Systems
  - Manage Virtual Network
  - ManageVirtualStorage
- Partition
  - Modify Partitions
  - Activate Partition
  - Close Vterm
  - Delete Partition
  - DLPAR Operations
  - Suspend Partition
  - View Partitions
  - View Profile
  - Open Vterm
  - Reboot Partition
  - RemoteRestartLPAR
  - Shutdown Partition
  - ViosAdminOp
  - Virtual IO Server Command
- HMC Console
  - Modify HMC Configuration
  - Change HMC File Systems
  - View HMC Configuration
  - View HMC File Systems

Additionally, the user's session timeout must be set to a minimum of `120 minutes`.

## Key in all the PIM configurations related to lpar, AI workload, etc in `config.ini`

## Run PIM lifecycle manager

  ```
  export PYTHONPATH=.
  python3 cmd/pim.py [launch,destroy,upgrade,rollback,update-compute,update-config,status]
  ```

## Available sub commands

  ```
  bash-5.2$ python3.9 cmd/pim.py -h
  usage: pim.py [-h] [--debug]
                {launch,destroy,upgrade,rollback,update-compute,update-config,status}
                ...

  PIM Partition Lifecycle Manager
  All the commands acts upon configuration provided in config.ini file
  All the commands supports re-run which means if user tries to rerun a particular command involving creating a new resource it picks up from where it left during last run or it picks the already created resource and proceed with the command execution

  positional arguments:
    {launch,destroy,upgrade,rollback,update-compute,update-config,status}
      launch              Setup PIM partition
      destroy             Destroy PIM partition and cleanup installation devices
      upgrade             Upgrade PIM partition's AI image to the latest version
      rollback            Rollback PIM partition's AI image to its previous version
      update-compute      Updates the cpu and memory configuration of the PIM partition
      update-config       Updates PIM partition's AI related configuration
      status              Status of PIM partition

  optional arguments:
    -h, --help            show this help message and exit
    --debug               Enable debug logging
  ```
  