#!/bin/bash

set -x

[ -f /etc/pim/email_ner.conf ] || touch /etc/pim/email_ner.conf
var_to_add=OPENAI_BASE_URL=$(jq -r '.openAIBaseURL' /etc/pim/pim_config.json)
sed -i "/^OPENAI_BASE_URL=.*/d"  /etc/pim/email_ner.conf && echo "$var_to_add" >> /etc/pim/email_ner.conf
