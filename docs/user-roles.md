# HMC User Roles

The HMC user must have either the default role hmcsuperadmin or mandatory task roles listed below.

**List of task roles required by user**

| HMC REST URI endpoints              |     HMC Operations                           |
| ------------------------------------| ---------------------------------------------|
| Managed System                      |      Create Partition                        |
|                                     |      View Managed Systems                    |
|                                     |      Manage Virtual Network                  |
|                                     |      ManageVirtualStorage                    |
|Partition                            |      Modify Partitions                       |
|                                     |      Activate Partition                      |
|                                     |      Close Vterm                             |
|                                     |      Delete Partition                        |
|                                     |      DLPAR Operations                        |
|                                     |      Suspend Partition                       |
|                                     |      View Partitions                         |
|                                     |      View Profile                            |
|                                     |      Open Vterm                              |
|                                     |      Reboot Partition                        |
|                                     |      RemoteRestartLPAR                       |
|                                     |      Shutdown Partition                      |
|                                     |      ViosAdminOp                             |
|                                     |      Virtual IO Server Command               |
|HMC Console                          |      Modify HMC Configuration                |
|                                     |      View HMC Configuration                  |
|                                     |      Change HMC File Systems                 |
|                                     |      View HMC File Systems                   |

**Additionally, the session timeout of user must be set to a minimum of 120 minutes**