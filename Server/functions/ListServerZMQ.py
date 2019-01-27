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

import logging
import requests
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ListServerClientZMQ(threading.Thread):
    def __init__(self, bdd, influxdb_url):
        threading.Thread.__init__(self)
        self.listServerZMQ = []
        self.listClientZMQ = []
        self.bdd = bdd
        self.influxdb_url = influxdb_url

    def run(self):
        while True:
            for clientZMQ in self.listClientZMQ:
                if clientZMQ.message is not None:
                    if not clientZMQ.message["influxdb"]:
                        if self.bdd.get_range_test_from_id(clientZMQ.message["id"], clientZMQ.message["id"]):
                            self.bdd.update_test("probe", clientZMQ.message["id"], self.format_for_bdd(clientZMQ.message))
                            clientZMQ.message = None
                    else:
                        if self.influxdb_url is not None and self.influxdb_url != "":
                            data = self.format_for_influx(clientZMQ.message)
                            self.send_to_influxdb(self.influxdb_url, data)
                            clientZMQ.message = None

                if clientZMQ.busy:
                    self.get("server", self.listClientZMQ.index(clientZMQ)).client["busy"] = True
                else:
                    self.get("server", self.listClientZMQ.index(clientZMQ)).client["busy"] = False
            time.sleep(1)

    def add(self, type, zmq):
        if type == "server":
            self.listServerZMQ.append(zmq)
        else:
            self.listClientZMQ.append(zmq)

    def get(self, type, id):
        if type == "server":
            return self.listServerZMQ[id]
        else:
            return self.listClientZMQ[id]

    def get_list_name(self):
        list_server_zmq_name = []
        for serverZMQ in self.listServerZMQ:
            list_server_zmq_name.append(serverZMQ.client["name"])
        return list_server_zmq_name

    def get_list_is_alive(self):
        list_server_zmq_is_alive = []
        for serverZMQ in self.listServerZMQ:
            list_server_zmq_is_alive.append(serverZMQ.is_alive())
        return list_server_zmq_is_alive

    def get_list_busy(self):
        list_server_zmq_busy = []
        for serverZMQ in self.listServerZMQ:
            list_server_zmq_busy.append(serverZMQ.client["busy"])
        return list_server_zmq_busy

    def get_list_uptime(self):
        list_server_zmq_uptime = []
        for serverZMQ in self.listServerZMQ:
            list_server_zmq_uptime.append(serverZMQ.uptime())
        return list_server_zmq_uptime

    def get_info_sondes(self):
        list_info_server_zmq = []
        for serverZMQ in self.listServerZMQ:
            list_info_server_zmq.append({
                                            "id": self.listServerZMQ.index(serverZMQ),
                                            "name": serverZMQ.client["name"],
                                            "is_alive": serverZMQ.is_alive(),
                                            "is_busy": serverZMQ.client["busy"],
                                            "autotest": serverZMQ.client["autotest"],
                                            "uptime": serverZMQ.uptime()
                                         })
        return list_info_server_zmq

    def get_nb_clients_alive(self):
        nb_clients_alive = 0
        for serverZMQ in self.listServerZMQ:
            if serverZMQ.is_alive():
                nb_clients_alive += 1
        return nb_clients_alive

    def get_nb_clients_alive_and_not_busy(self):
        nb_clients_not_busy = 0
        for serverZMQ in self.listServerZMQ:
            if serverZMQ.is_alive() and not serverZMQ.client["busy"]:
                nb_clients_not_busy += 1
        return nb_clients_not_busy

    def send_to_influxdb(self, url, data):
        try:
            r = requests.post(url, data=data)
            if r.status_code == 204:
                logger.info("Data send to InfluxDB URL --> %s\nData --> %s", self.influxdb_url, data)
            else:
                logger.error("Error can't send data to InfluxDB URL --> %s\nHTTP Error code --> %s", self.influxdb_url, r.status_code)
        except Exception as e:
            logger.error("Error can't send data to InfluxDB URL --> %s\nError --> %s", self.influxdb_url, e)

    @staticmethod
    def speedof(num, suffix='b/s'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Y', suffix)

    @staticmethod
    def format_for_bdd(message):
        if message["packet_loss"] != "":
            message["packet_loss"] = "Packet loss: " + str(
                message["packet_loss"]["packet_number"]) + ", Percentage of lost: " + str(
                message["packet_loss"]["packet_percent"]) + "%"
        else:
            message["packet_loss"] = ""
        if message["ping"] != "":
            message["ping"] = "Min ping: " + str(message["ping"]["min"]) + ", Max ping: " + str(
                message["ping"]["max"]) + ", Average ping: " + str(message["ping"]["avg"])
        else:
            message["ping"] = ""
        if message["speedtest"] != "":
            for speedtest in ["download", "upload"]:
                if message["speedtest"][speedtest] != "":
                    if message["speedtest"][speedtest]["status"] == "success":
                        speedtest_result = "min=" + ListServerClientZMQ.speedof(message["speedtest"][speedtest]["result"]["min"]) \
                                    + ", avg=" + ListServerClientZMQ.speedof(message["speedtest"][speedtest]["result"]["avg"]) \
                                    + ", max=" + ListServerClientZMQ.speedof(message["speedtest"][speedtest]["result"]["max"])
                        speedtest_json_raw = message["speedtest"][speedtest]["json"]
                    else:
                        speedtest_result = "Error : " + message["speedtest"][speedtest]["message"]
                        speedtest_json_raw = ""
                else:
                    speedtest_result = ""
                    speedtest_json_raw = ""
                message[speedtest] = speedtest_result
                message[speedtest + "_json_raw"] = speedtest_json_raw
        else:
            message["download"] = ""
            message["download_json_raw"] = ""
            message["upload"] = ""
            message["upload_json_raw"] = ""
        return message

    @staticmethod
    def format_for_influx(message):
        data = ""
        if message["ping"] != "":
            data = data + "ping,probe=" + message["probe_name"] + " min=" + str(message["ping"]["min"]) \
                   + ",avg=" + str(message["ping"]["avg"]) \
                   + ",max=" + str(message["ping"]["max"]) + "\n"
        if message["jitter"] != "":
            data = data + "jitter,probe=" + message["probe_name"] + " value=" + str(message["jitter"]) + "\n"
        if message["packet_loss"] != "":
            data = data + "packet_loss,probe=" + message["probe_name"] + " number=" + str(message["packet_loss"]["packet_number"]) \
                   + ",percent=" + str(message["packet_loss"]["packet_percent"]) + "\n"
        if message["mos"] != "":
            data = data + "mos,probe=" + message["probe_name"] + " value=" + str(message["mos"]) + "\n"
        if message["packet_number"] != "":
            data = data + "packet_number,probe=" + message["probe_name"] + " value=" + str(message["packet_number"]) + "\n"
        if message["packet_timeout"] != "":
            data = data + "packet_timeout,probe=" + message["probe_name"] + " value=" + str(message["packet_timeout"]) + "\n"
        if message["speedtest"] != "":
            for speedtest in ["download", "upload"]:
                if message["speedtest"][speedtest] != "":
                    if message["speedtest"][speedtest]["status"] == "success":
                        data = data + speedtest + ",probe=" + message["probe_name"] + " min=" + str(message["speedtest"][speedtest]["result"]["min"]) \
                               + ",avg=" + str(message["speedtest"][speedtest]["result"]["avg"]) \
                               + ",max=" + str(message["speedtest"][speedtest]["result"]["max"]) + "\n"
        if message["speedtest_option"] != "":
            data = data + "iperf_option,probe=" + message["probe_name"] + " value=\"" + str(message["speedtest_option"]) + "\"\n"
        if message["comment"] != "":
            data = data + "comment,probe=" + message["probe_name"] + " value=\"" + message["comment"] + "\"\n"
        return data
