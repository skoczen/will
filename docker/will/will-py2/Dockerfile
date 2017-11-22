#Pull from will-base
FROM heywill/will-base:2.7-alpine
ARG repo=https://github.com/skoczen/will.git
ARG branch=master
# Maintainer
# ----------
LABEL maintainer=mlove@columnit.com 

RUN pip install git+$repo@$branch 
WORKDIR $_WILL_HOME
RUN yes | generate_will_project
CMD $_WILL_HOME/run_will.py
