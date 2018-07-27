#Pull from pcobot-base
FROM pastorhudson/pcobot:base
ARG repo=https://github.com/pastorhudson/pcobot.git
ARG branch=master
ARG backends="Slack Shell"
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
LABEL maintainer=ron@pastorhudson.com

RUN pip install git+https://github.com/pastorhudson/pcobot.git@$branch
RUN pip install git+https://github.com/pastorhudson/pypco.git
WORKDIR $_WILL_HOME
RUN generate_will_project  --backends $backends
CMD $_WILL_HOME/run_will.py