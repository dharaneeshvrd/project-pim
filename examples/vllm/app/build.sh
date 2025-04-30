#!/bin/bash

set -x

TAG=$(curl -s https://api.github.com/repos/vllm-project/vllm/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

curl -L -o vllm-${TAG}.tar.gz https://github.com/vllm-project/vllm/archive/refs/tags/${TAG}.tar.gz

tar xzf vllm-${TAG}.tar.gz

cd vllm-${TAG#v}

podman build -t localhost/vllm -f docker/Dockerfile.ppc64le .

