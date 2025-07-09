# PIM Builder guide

A builder is a system integrator(SI) or an ISV who wishes to deploy AI solutions on IBMi/AIX/Linux environment using PIM. This guide helps SIs to build PIM image for AI workloads of their choice using base image.
A few Inferencing AI workloads like entity extraction, fraud detection are provided for PIM provisioning as reference [here](../examples/). LLM is not mandatory for applications based on machine learning models.

## PIM base image
To decouple/ease building of reference AI workloads, base PIM image is built on RHEL bootc image. It wraps cloud-init tool to perform initial network/ssh configurations and base config service.
This base image is constant across different AI workloads/usecases.  
Steps to build PIM image is captured [here](../base-image/README.md).

**NOTE: Builder needs to have a RHEL/Centos/Fedora based VM/lpar to build PIM base images and custom AI workload images. For RHEL base image, user needs to have RHEL machine with subscription activated. Base image for remaining OSs can be built on either centos or fedora VM**

## Building PIM based AI workload image
Any AI workload image/stack that needs to be provisioned on IBM environemnt needs to have [app_structure](app_structure.png)

- app - application/workload specific buisiness logic and builds the application container image.
- entity.container - A systemd service file to pull the AI workload image(entity extraction) from a registry during runtime and runs the AI application(entity extraction) as container. Make sure all container related inputs are added in `Container` block.
- Containerfile - Base image should be a PIM base image. Should have instructions to compile the app and provide dependencies for running the application binaries. Make sure entity.container file is also made part of the Containerfile.

Build the PIM based AI workload image using `podman build` command

A reference to the guide on building AI workload is here [examples](../examples/README.md)
