#Pull CENTOS
FROM python:2.7-stretch

# Maintainer
# ----------
MAINTAINER mlove@columnit.com 

ENV _WILL_HOME=/opt/will

RUN mkdir -p $_WILL_HOME

WORKDIR $_WILL_HOME
RUN pip install will

#CMD $_WILL_HOME/start_dev_will.py

CMD /bin/bash
