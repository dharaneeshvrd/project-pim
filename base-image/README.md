# Base PIM Image

## Containerfile
```Dockerfile
FROM registry.redhat.io/rhel9/rhel-bootc:9.6-1747275992
```
Use bootc base image from officially built rhel container image [here](https://catalog.redhat.com/software/containers/rhel9/rhel-bootc/6605573d4dbfe41c3d839c69?architecture=ppc64le&image=68255270360faaf4e6db2240&container-tabs=gti&gti-tabs=red-hat-login) 
You need Redhat account to get the credentials to pull the image

```Dockerfile
RUN dnf -y install cloud-init && \
    ln -s ../cloud-init.target /usr/lib/systemd/system/default.target.wants && \
    rm -rf /var/{cache,log} /var/lib/{dnf,rhsm}
COPY usr/ /usr/
```
Install cloud-init to configure AI image and PIM partition's network and user

```Dockerfile
COPY base_config.sh /usr/bin/
COPY base_config.service /etc/systemd/system

RUN systemctl unmask base_config.service
RUN systemctl enable base_config.service
```
Systemd service to setup pimconfig like copying cloud init config and pim config files to respective directory

## Build

Run the build in a RHEL machine with proper subscription activated. `podman build` will use the build machine's host subscription to install pkgs in PIM image.

```shell
podman build -t localhost/pim-base .

podman tag localhost/pim-base na.artifactory.swg-devops.com/sys-pcloud-docker-local/devops/pim/base
podman push na.artifactory.swg-devops.com/sys-pcloud-docker-local/devops/pim/base
```
