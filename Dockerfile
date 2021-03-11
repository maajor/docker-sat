FROM ubuntu:bionic

RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse" > /etc/apt/sources.list
RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse" >> /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y --fix-missing\
    sudo \
    python3-pip \
    libglu1-mesa \
    libxrandr2 \
    libsm6 \
    xvfb \
    libfontconfig \
    libxkbcommon-x11-0

# https://forum.qt.io/topic/120349/run-qt-gui-application-inside-docker/13
ENV DISPLAY=:1

# copy installer
RUN mkdir /satInstaller && mkdir /opt/Allegorithmic
COPY ./installer/Substance_Automation_Toolkit* /satInstaller
RUN tar -xvf /satInstaller/Substance_Automation_Toolkit* -C /opt/Allegorithmic && rm -r /satInstaller

# install
WORKDIR /opt/Allegorithmic/Substance_Automation_Toolkit/Python API/
RUN pip3 install Pysbs*.whl
ENV PATH $PATH:"/opt/Allegorithmic/Substance_Automation_Toolkit"
ENV SDAPI_SATPATH "/opt/Allegorithmic/Substance_Automation_Toolkit"
WORKDIR /

COPY ./src /home
WORKDIR /the/workdir/path