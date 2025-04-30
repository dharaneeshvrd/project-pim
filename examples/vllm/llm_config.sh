#!/bin/bash

set -x

echo LLM_ARGS=$(jq -r '.llmArgs' /etc/pim/pim_config.json) > /etc/pim/env.conf
echo LLM_IMAGE=$(jq -r '.llmImage' /etc/pim/pim_config.json) >> /etc/pim/env.conf
echo REGISTRY_AUTH_FILE=/etc/pim/auth.json >> /etc/pim/env.conf

