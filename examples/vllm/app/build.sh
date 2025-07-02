#!/bin/bash

stream=$1

if [[ ${stream} == "" || ${stream} == "--help" || ${stream} == "-h" ]]; then
	echo "./build.sh <stream>"
	echo "stream - mention from which stream you want to build your vLLM image. Options: release, main"
	echo "release - you can pass release version after stream like this and vLLM will get built on the specified released version" 
	echo "i.e. ./build.sh release 0.8.5.post1"
	echo "main - it will build the vLLM application from main branch"
	echo "i.e. ./build.sh main"
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
