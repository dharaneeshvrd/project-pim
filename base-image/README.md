# Base PIM Image

## Containerfile
```
FROM registry.stage.redhat.io/rhel9/rhel-bootc:9.6
```
Use bootc base image from officially built rhel container image [here](https://catalog.redhat.com/search?gs&q=bootc) 

```
ARG RH_SUBS_USERNAME
ARG RH_SUBS_PASSWORD

RUN subscription-manager register --username=$RH_SUBS_USERNAME --password=$RH_SUBS_PASSWORD --auto-attach
```
Since we are using rhel image need to activate subscription-manager which requres subscription username and password

```
RUN dnf -y install cloud-init && \
    ln -s ../cloud-init.target /usr/lib/systemd/system/default.target.wants && \
    rm -rf /var/{cache,log} /var/lib/{dnf,rhsm}
COPY usr/ /usr/
```
Install cloud-init to configure AI image and PIM partition's network and user

```
COPY get_pimconfig.sh /usr/bin/
COPY pimconfig.service /etc/systemd/system

RUN systemctl unmask pimconfig.service
RUN systemctl enable pimconfig.service
```
Systemd service to setup pimconfig like copying cloud init config and pim config files to respective directory

```
COPY vllm.container /usr/share/containers/systemd
```
`vllm.container` will be converted to systemd service that runs vLLM image passed via pim config which copied in previous step

## Build

```
export RH_SUBS_USERNAME=""
export RH_SUBS_PASSWORD=""

podman build --security-opt label=type:unconfined_t  --cap-add=all   --device /dev/fuse --build-arg RH_SUBS_USERNAME=$RH_SUBS_USERNAME --build-arg RH_SUBS_PASSWORD=$RH_SUBS_PASSWORD -t localhost/pim-bootc .

podman tag localhost/pim-bootc na.artifactory.swg-devops.com/aionpower/pim:9.6
podman push na.artifactory.swg-devops.com/aionpower/pim:9.6

```

## Usage
Once its built, it can be used in [config.ini](../../config.ini) `ai.workload-image` field to use it in the automation to bringup the PIM partition
