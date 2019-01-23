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

import logging
import threading
import time
from datetime import datetime
import zmq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientZMQREQ (threading.Thread):
    def __init__(self, name, client_address, client_port, server_address, server_port):
        threading.Thread.__init__(self)
        self.name = name
        self.client_address = client_address
        self.client_port = client_port
        self.server_address = server_address
        self.server_port = server_port
        self.message = None
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

    def run(self):
        self.socket.connect("tcp://%s:%s" % (self.server_address, self.server_port))
        logger.info("Client connected to --> %s:%s", self.server_address, self.server_port)
        self.hello()

    def send_data(self, json_data):
        self.socket.send_json(json_data)
        self.message = self.socket.recv_json()
        logger.info("Time: %s\n Request: %s\n", datetime.now().replace(microsecond=0), self.message)

    def hello(self):
        self.send_data({"type": "hello", "name": self.name, "address": self.client_address, "port": self.client_port})
        time.sleep(5)
        self.hello()
