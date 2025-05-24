#!/bin/bash

git clone -b support-ppc64le git@github.ibm.com:redstack-power/spyre.git
cd spyre/

podman build -t localhost/email-ner -f email-ner-demo/Containerfile.ppc64le .
