# Power Inference Microservices (PIM)

PIM enables installation of AI environment with minimal steps on IBM core environments like IBMi, AIX or Linux. PIM solution leverages bootable containers(bootc), a modern tool for deploying and configuring immutable linux systems.

PIM provides end-to-end solution for AI stack installation by logical partition creation, network and storage attachment and boots partition with specified AI stack image in the configuration.

![alt text](docs/architecture.png)

## Key highlights of PIM solution
- Seamless Update: Systems updates are automatic if newer version of the image is publically available. Otherwise, when user manually triggers upgrade the system updates are pulled from the configured registry. After applying the new version of the image and upon reboot, system boots with newer version of the AI stack.
- Rollback: bootc preserves state of the system. In case of disruption in Updates, system can be rolled back to prevision version.
- Makes admin's management simple by easing day 2 operations like monitor, upgrade and manage.
- Provides end-to-end software lifecycle management operations like `launch`, `destroy`, `update-config`, `update-compute`, `rollback` and `destroy`
- Provides AI inferencing capability on CPU currently. Aim to provide inferencing based on AI accelerator in future.
- PIM currently supports IBMi and Linux OS environments. AIX OS will be supported later.

## PIM Personas
PIM has 2 personas namely builder and deployer.
- Builder: An ISV or System Integrator who builds AI stack including the workload of their choice. Refer [builder-guide.md](docs/builder-guide.md) for more details.
- Deployer: End User who uses PIM solution to deploy the AI solution in IBM core environment. Refer [deployer-guide.md](docs/deployer-guide.md) for more details.

## Component Versions
Below are the minimum supported versions of critical components of PIM

| Component                                    |             Version                                 |
| -------------------------------------------- | --------------------------------------------------- |
| Host Management Console(HMC)                 |      1061 for latest P10, 1110 for P11              |
| Partition Firmware(PFW)                      |      1110(P11) and 1060(P10)                        |
| IBMi                                         |      7.5                                            |
| Linux                                        |      Rhel 9.6(bootc) and Fedora 42(bootstrap ISO)   |
| Virtual IO Server(VIOS)                      |      4.1.1.0                                        |
