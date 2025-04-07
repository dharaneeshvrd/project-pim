#!/bin/bash

set -x

mkdir -p /tmp/pim

mount -t iso9660 -o loop /dev/sr1 /tmp/pim
if [ ! -e /tmp/pim/99_custom_network.cfg ]; then
    umount /tmp/pim
    rm -rf /tmp/pim
    mkdir /tmp/pim
    mount -t iso9660 -o loop /dev/sr0 /tmp/pim
fi

mkdir -p /etc/pim
cp /tmp/pim/99_custom_network.cfg /etc/cloud/cloud.cfg.d/
cp /tmp/pim/pim_config.json /etc/pim/
cp /tmp/pim/auth.json /etc/pim/

echo LLM_ARGS=$(jq -r '.llmArgs' /etc/pim/pim_config.json) > /etc/pim/env.conf
echo LLM_IMAGE=$(jq -r '.llmImage' /etc/pim/pim_config.json) >> /etc/pim/env.conf
echo REGISTRY_AUTH_FILE=/etc/pim/auth.json >> /etc/pim/env.conf