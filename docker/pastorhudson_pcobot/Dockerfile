# This is edited to pull the pcobot from github rather than will bot.
# This is the docker file pastorhudson/pcobot is built on.
# It still runs on the will-base image.

#Pull from will-base
FROM heywill/will-base:3.7-alpine
ARG repo=https://github.com/pastorhudson/pcobot.git
ARG branch=dev
ARG backends="Slack"
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

RUN pip install git+https://github.com/pastorhudson/pcobot.git@$branch 
RUN pip install git+https://github.com/pastorhudson/pypco.git
WORKDIR $_WILL_HOME
RUN generate_will_project  --backends $backends
CMD $_WILL_HOME/run_will.py
