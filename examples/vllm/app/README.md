# Build vLLM

Run `./build.sh` in a P10 Linux machine to build https://github.com/vllm-project/vllm from scratch to use it as a inference server in PIM

### Prerequisite
- Podman
- Git

### Build
```
$ ./build.sh # Clones latest release into current dir and builds a container image called `localhost/vllm`
$
$ podman tag localhost/vllm <your_registry>/vllm
$
$ podman push <your_registry>/vllm
```
