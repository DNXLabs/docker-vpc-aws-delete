FROM  python:alpine3.17

RUN apk add --no-cache bash
RUN python3 -m pip install -U --force-reinstall pip \
    && python3 -m pip install -U --force-reinstall awscli

WORKDIR /work
COPY requirements.txt aws-vpc.py /work/
RUN pip3 install -r requirements.txt