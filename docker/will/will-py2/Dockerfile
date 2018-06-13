#Pull from will-base
FROM heywill/will-base:2.7-alpine
ARG repo=https://github.com/skoczen/will.git
ARG branch=master
ARG backends="HipChat Rocket.chat Slack Shell"
ENV PACKAGES="\
  dumb-init \
  bash \
  ca-certificates \
  python2 \
  py-setuptools \
  libffi-dev \
"
# Maintainer
# ----------
LABEL maintainer=mlove@columnit.com 

RUN pip install git+$repo@$branch 
WORKDIR $_WILL_HOME
RUN generate_will_project  --backends $backends
CMD $_WILL_HOME/run_will.py
