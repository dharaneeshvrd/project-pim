#!/bin/bash

stream=$1

if [[ ${stream} == "" || ${stream} == "--help" || ${stream} == "-h" ]]; then
	echo "./build.sh <stream>"
	echo "stream - release, main - mention from which stream you want to build your vLLM image"
	echo "In case of 'release' stream, you can pass release version after stream like this" 
	echo "./build.sh release 0.8.5.post1"
	exit
fi

if [[ ${stream} == "release" ]]; then
	branch=$2
	if [[ ${branch} == "" ]]; then
		branch=$(curl -s https://api.github.com/repos/vllm-project/vllm/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
	fi
fi

if [[ ${stream} == "main" ]]; then
	branch="main"
fi

git clone -b ${branch} https://github.com/vllm-project/vllm.git
cd vllm

podman build -t localhost/vllm -f docker/Dockerfile.ppc64le .
