# ----------------------------------------------------------------------------
# Copyright © Lyon e-Sport, 2018
#
# Contributeur(s):
#     * Ortega Ludovic - ludovic.ortega@lyon-esport.fr
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

import os
import json
import re

from functions.ServerZMQ import ServerZMQREP
from functions.ClientZMQ import ClientZMQREQ

regex_ip = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
regex_name = r"^[0-9a-zA-Z -_]{4,20}$"

# get client ZMQ configuration

# get clientZMQ config
clientZMQ_config = {
                       "probe_client": {
                            "name": os.environ.get("PROBE_NAME", None),
                            "address": os.environ.get("PROBE_IP", None),
                            "port": os.environ.get("PROBE_PORT", None)
                       },

                       "probe_server": {
                            "address": os.environ.get("SERVER_IP", None),
                            "port": os.environ.get("SERVER_PORT", None)
                       }
                    }
try:
    with open('config/clientZMQ.json') as json_data_file:
        clientZMQ_config.update(json.load(json_data_file))
except Exception as error:
        pass
try:
    if not re.match(regex_name, clientZMQ_config["probe_client"]["name"])\
            or not re.match(regex_ip, clientZMQ_config["probe_client"]["address"]) \
            or not re.match(regex_ip, clientZMQ_config["probe_server"]["address"])\
            or not (clientZMQ_config["probe_client"]["port"] >= 1 and clientZMQ_config["probe_client"]["port"] <= 65535) \
            or not (clientZMQ_config["probe_server"]["port"] >= 1 and clientZMQ_config["probe_server"]["port"] <= 65535):
        raise Exception('clientZMQ.json wrong format')
except Exception as error:
    print('Caught this error: ' + repr(error))
    exit()

serverZMQ = ServerZMQREP(clientZMQ_config["probe_client"]["port"])
serverZMQ.start()
clientZMQ = ClientZMQREQ(clientZMQ_config["probe_client"]["name"], clientZMQ_config["probe_client"]["address"], clientZMQ_config["probe_client"]["port"], clientZMQ_config["probe_server"]["address"], clientZMQ_config["probe_server"]["port"])
clientZMQ.start()

