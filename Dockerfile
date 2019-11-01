FROM python:3.6
MAINTAINER Angeline Meitzler

ENV INSTALL_PATH /django-copy3
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

RUN apt-get -y update
RUN apt-get install -y python-pip
RUN pip install --upgrade pip

RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python setup.py install --yes USE_AVX_INSTRUCTIONS


ADD . /project/media


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install scipy




ENV DJANGO_SETTINGS_MODULE=config.settings.production



COPY . .
