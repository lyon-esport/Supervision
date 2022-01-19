FROM python:3.9-alpine

LABEL maintainer="Ludovic Ortega ludovic.ortega@lyon-esport.fr"

# update package
RUN apk update

# install requirement for zmq
RUN apk add build-base build-base libzmq musl-dev python3 python3-dev zeromq-dev

# install gunicorn
RUN pip3 install gunicorn

# copy program
COPY * /app/server_supervision/

# set workdir
WORKDIR /app/server_supervision/

# remove useless file
RUN rm lazy_server_windows.ps1

# install dependencies
RUN pip3 install -r requirements.txt

# create database
RUN python3 database_setup.py

CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:80"]