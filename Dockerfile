FROM ubuntu:22.04
SHELL ["/bin/bash", "-c"]

LABEL maintainer="Nick DiNapoli <nmd67@cornell.edu>"

ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && \
    apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.8 \
    python3.8-distutils \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

CMD /bin/bash
