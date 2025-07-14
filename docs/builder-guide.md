# PIM Builder guide

Builder is someone who wishes to deploy an AI solution on IBMi/AIX/Linux environments using PIM. This guide helps to build a PIM image for AI workloads of their choice.
A few Inferencing AI workloads like entity extraction, fraud detection are provided for PIM provisioning as reference [here](../examples/). LLM is not mandatory for applications based on machine learning models.

## Base image
Base PIM image can be built on RHEL/Fedora/CentOS bootc image. Officially PIM uses RHEL bootc base image. It wraps cloud-init tool to perform initial network/ssh configurations and base config service. To decouple/ease building of AI workloads, base image is built separately.
This base image is constant across different AI workloads/usecases.  
Steps to build PIM image is captured [here](../base-image/README.md).

**NOTE: Builder needs to use a RHEL/CentOS/Fedora based VM/lpar to build the PIM base images and custom AI workload images. For RHEL base image, user needs to use RHEL node with subscription activated. Base image for remaining OSs can be built on either centos or fedora VM**

## AI image
AI image holds steps to run the AI application when it is deployed on a partition via PIM, you need to pass this AI image only to the PIM deployer utility. It usually follows below [application structure](app_structure.png) to get it deployed via PIM. 

- app - AI application specific business logic and contains build scripts to build the container image of the AI application.
- entity.container - A systemd service file to pull the AI workload image(entity extraction) from a registry during runtime and runs the AI application(entity extraction) as container. Make sure all container related inputs are added in `Container` block.
- Containerfile - Base image should be a PIM base image. Contains copy steps to copy the entity.container and configuration scripts to run them when the system starts.

Build the PIM based AI workload image using `podman build` command

A reference guide on building AI workload is here [examples](../examples/README.md)
