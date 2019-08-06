FROM python:3.7-alpine

LABEL maintainer="Ludovic Ortega ludovic.ortega@lyon-esport.fr"

# update package
RUN apk update

# install iperf3
RUN apk add iperf3

# install requirement for zmq
RUN apk add build-base build-base libzmq musl-dev python3 python3-dev zeromq-dev

# copy program
COPY * /app/client_supervision/

# set workdir
WORKDIR /app/client_supervision/

# remove useless file
RUN rm iperf3.exe cygwin1.dll

# install dependencies
RUN pip3 install -r requirements.txt

CMD ["python3", "/app/client_supervision/client.py"]