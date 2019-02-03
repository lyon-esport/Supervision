# ----------------------------------------------------------------------------
# Copyright © Lyon e-Sport, 2018
#
# Contributeur(s):
#     * Ortega Ludovic - ludovic.ortega@lyon-esport.fr
#     * Etienne Guilluy - etienne.guilluy@lyon-esport.fr
#     * Barbou Théo - theobarbou@gmail.com
#     * Dupessy Clément - clement07131@hotmail.fr
#     * Julian Marty - julian.marty83@gmail.com
#
# Ce logiciel, Supervision, est un programme informatique servant à lancer des tests réseaux
# (ping/jitter/packet loss/mos/download/upload) sur des sondes via un site web.
#
# Ce logiciel est régi par la licence CeCILL soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
# sur le site "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement,
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
# pris connaissance de la licence CeCILL, et que vous en avez accepté les
# termes.
# ----------------------------------------------------------------------------

FROM python:3.6-alpine as build

MAINTAINER Ludovic Ortega ludovic.ortega@lyon-esport.fr

# update package
RUN apk update

# install gcc
RUN apk add build-base

# install git
RUN apk add git

# download supervision project
RUN git clone https://github.com/lyon-esport/Supervision.git

# copy file to /app/
RUN mkdir -p /app/server_supervision/ && mv Supervision/Server/* /app/server_supervision/

# remove useless file
RUN rm -Rf ./Supervision /app/server_supervision/lazy_server_windows.ps1

# install dependencies
RUN pip3 install -r ./app/server_supervision/requirements.txt

FROM python:3.6-alpine

# update package
RUN apk update

# install gcc
RUN apk add build-base

# install gunicorn
RUN pip3 install gunicorn

# copy server supervision
COPY --from=build /app/server_supervision/ /app/server_supervision/

# copy python library
COPY --from=build  /usr/local/lib/python3.6/site-packages/ /usr/local/lib/python3.6/site-packages/

# set config
ENV SERVER_ZMQ_FIRST_PORT 30000
ENV SERVER_ZMQ_NB_PORT 10
ENV INFLUXDB_URL http://127.0.0.1:8086/write?db=prober

# expose server port
EXPOSE 80 30000-30010

# set workdir
WORKDIR /app/server_supervision/

# create database
RUN python3 database_setup.py

CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:80"]