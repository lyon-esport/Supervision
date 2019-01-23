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
from datetime import datetime
import time
import threading
import zmq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientZMQREQ(threading.Thread):
    def __init__(self, timeout):
        threading.Thread.__init__(self)
        self.busy = False
        self.server_address = None
        self.server_port = None
        self.json_data = None
        self.message = None
        self.context = None
        self.socket = None
        self.timeout = timeout

    def start_test(self, server_address, server_port, json_data):
        self.busy = True
        self.server_address = server_address
        self.server_port = server_port
        self.json_data = json_data
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.start()

    def run(self):
        self.socket.connect("tcp://%s:%s" % (self.server_address, self.server_port))
        logger.info("Client connected to --> %s:%s", self.server_address, self.server_port)
        time.sleep(1)
        self.socket.send_json(self.json_data)
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        if poller.poll(self.timeout * 1000):
            self.message = self.socket.recv_json()
            logger.info("Time: %s\n Request: %s\n", datetime.now().replace(microsecond=0), self.message)
        else:
            self.message = {
                            "id": self.json_data["id"],
                            "ping": "",
                            "jitter": "",
                            "packet_loss": "",
                            "mos": "",
                            "speedtest": "",
                            "status": "error"
                            }
            logger.info("Time: %s\n Request: Timeout :(\n", datetime.now().replace(microsecond=0))
        self.busy = False
        threading.Thread.__init__(self)

