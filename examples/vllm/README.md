# vLLM

Builds vLLM inference server on top of base image built here https://github.ibm.com/project-pim/base-images

### Config
Since vLLM AI image can be used as a base for many LLM inferencing applications like chatbot, entity extraction and many more, provided below configuration to tune the vLLM engine as per the AI use case. 

This can be fed into the application via `config-json` explained [here](../../docs/configuration-guide.md#ai)

#### llmImage
vLLM container image built using app section [here](app/README.md)
#### llmArgs
Args you can pass it to your vLLM inference engine
#### llmEnv
Env vars that you want to set while running vLLM inference engine

**Sample config:**
```ini
config-json = """
  {
        "llmImage": "na.artifactory.swg-devops.com/sys-pcloud-docker-local/devops/pim/apps/vllm",
        "llmArgs": "--model ibm-granite/granite-3.2-8b-instruct --max-model-len=26208 --enable-auto-tool-choice --tool-call-parser granite",
        "llmEnv": "OMP_NUM_THREADS=16"
  }
  """
```

### Build
**Step 1: Build Base image**
Follow the steps provided [here](../../base-image/README.md) to build the base image.

**Step 2: Build vLLM image**
Ensure to replace the `FROM` image with the base image you have built before building this image.
```shell
podman build -t <your_registry>/vllm

podman push <your_registry>/vllm
```
