# Build email-ner image

Run `./build.sh` in a Power Linux machine to build https://github.ibm.com/redstack-power/spyre to extract entities from an email

### Prerequisite
- Podman
- Git

### Build
```shell
./build.sh # Clones spyre repo and builds a container image called `localhost/email-ner`

podman tag localhost/email-ner <your registry>/pim:email-ner-app
podman push <your registry>/pim:email-ner-app
```
