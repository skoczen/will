#Pull CENTOS
FROM python:2.7-stretch

# Maintainer
# ----------
MAINTAINER mlove@columnit.com 

ENV _WILL_HOME=/opt/will

RUN mkdir -p $_WILL_HOME

RUN pip install will

WORKDIR $_WILL_HOME
RUN generate_will_project
CMD $_WILL_HOME/run_will.py
