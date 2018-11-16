# PULL python
FROM python:3.6.6-alpine

# Maintainer
LABEL maintainer="ron@pastorhudson.com"

ENV _WILL_HOME=/opt/will

RUN mkdir -p $_WILL_HOME

RUN apk add --no-cache git build-base libffi-dev openssl-dev