#!/bin/bash

set -x

LLM_ENV=$(jq -r '.llmEnv' /etc/pim/pim_config.json)
IFS=',' read -ra envs <<< "$LLM_ENV"
for env in "${envs[@]}"; do
    echo "$env" >> /etc/pim/env.conf
done

echo LLM_ARGS=$(jq -r '.llmArgs' /etc/pim/pim_config.json) >> /etc/pim/env.conf
echo LLM_IMAGE=$(jq -r '.llmImage' /etc/pim/pim_config.json) >> /etc/pim/env.conf

mkdir /var/huggingface
echo HF_HUB_CACHE=/var/huggingface >> /etc/pim/env.conf

echo REGISTRY_AUTH_FILE=/etc/pim/auth.json >> /etc/pim/env.conf
