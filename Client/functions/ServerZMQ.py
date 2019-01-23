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
import datetime
import zmq

# import Test functions
from functions.test import start_standard_test, start_speedtest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServerZMQREP (threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.message = None
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

    def run(self):
        self.socket.bind('tcp://*:{}'.format(self.port))
        logger.info("Server started on port --> %s", self.port)
        while True:
            self.message = self.socket.recv_json()
            logger.info("Time: %s\n Request: %s\n", datetime.datetime.now().replace(microsecond=0), self.message)
            if self.message["type"] == "test":
                self.start_test()

    def start_test(self):
        packet_number = self.message["packet_number"]  # Number of packet sent
        packet_timeout = self.message["packet_timeout"]  # Maximum timeout between each test
        src_addr = ""  # Source address
        src_name = "Probe"  # Source name
        dest_addr = self.message["standard_test_target"]  # Ping adress
        dest_name = self.message["standard_test_target"]  # Name Desination
        output = "return"  # Output choice
        rrd_file = None  # RRD file

        if dest_addr != "":
            ping, jitter, packet_loss, mos = start_standard_test(packet_number, packet_timeout, src_addr, src_name,
                                                                   dest_addr, dest_name, output, rrd_file)
        else:
            ping, jitter, packet_loss, mos = "", "", "", ""

        type_speedtest = self.message["speedtest_choice"]  # Speedtest choice
        dest_addr_speedtest = self.message["speedtest_target"]["ip"]  # Speedtest address
        dest_port_speedtest = str(self.message["speedtest_target"]["port"])  # Speedtest port
        option_speedtest = self.message["speedtest_option"]  # Speedtest option

        if dest_addr_speedtest != "":
            speedtest = start_speedtest(type_speedtest, dest_addr_speedtest, dest_port_speedtest, option_speedtest)
        else:
            speedtest = ""
        logger.info("Ping: %s\n Jitter: %s\n Packet loss:%s\n Speedtest:%s\n MOS:%s\n", ping, jitter, packet_loss,
                    speedtest, mos)

        self.socket.send_json({
                                "type": "result",
                                "id": self.message["id"],
                                "probe_name": self.message["probe_name"],
                                "ping": ping,
                                "jitter": jitter,
                                "packet_loss": packet_loss,
                                "mos": mos,
                                "packet_number": self.message["packet_number"],
                                "packet_timeout": self.message["packet_timeout"],
                                "speedtest": speedtest,
                                "speedtest_option": self.message["speedtest_option"],
                                "comment": self.message["comment"],
                                "influxdb": self.message["influxdb"],
                                "status": "done"
                                })

