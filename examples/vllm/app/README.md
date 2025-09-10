# Build vLLM

Run `./build.sh` in a P10 Linux machine to build https://github.com/vllm-project/vllm from scratch to use it as a inference server in PIM

### Prerequisite
- Podman
- Git

### Build
```shell
./build.sh # Clones latest release into current dir and builds a container image called `localhost/vllm`
 
./build.sh -h
./build.sh <stream>
stream - mention from which stream you want to build your vLLM image. Options: release, main
release - you can pass release version after stream like this and vLLM will get built on the specified released version
i.e. ./build.sh release 0.8.5.post1
main - it will build the vLLM application from main branch
i.e. ./build.sh main

podman tag localhost/vllm <your registry>/pim:vllm-app
podman push <your registry>/pim:vllm-app
```
