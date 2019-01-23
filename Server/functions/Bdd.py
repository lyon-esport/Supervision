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

import sqlite3
import re
from datetime import datetime


class Bdd:
    def __init__(self, filename, template_config, regex_id, regex_ip, regex_port, regex_name, regex_comment):
        self.filename = filename
        self.connection = None
        self.cursor = None
        self.template_config = template_config
        self.regex_id = regex_id
        self.regex_ip = regex_ip
        self.regex_port = regex_port
        self.regex_name = regex_name
        self.regex_comment = regex_comment

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.filename, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
        except Exception:
            print("Error")
            self.connection.rollback()

    def execute(self, sql, data):
        try:
            self.cursor.execute(sql, data)
            self.commit()
        except Exception as e:
            print("Error : ", e)
            self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def add_server(self, server_name, server_ip, server_port, standard_test, speedtest):
        if server_port != "":
            if not re.match(self.regex_port, server_port):
                return self.return_message('Error !', 'You can not update a server that does not exist', 'error', True,
                                           True)
        if re.match(self.regex_name, server_name) and re.match(self.regex_ip, server_ip):
            data = {"server_name": server_name, "server_ip": server_ip, "server_port": server_port, "standard_test": standard_test, "speedtest": speedtest}
            sql = ("""
                    INSERT INTO server(server_name, server_ip, server_port, standard_test, speedtest) 
                    VALUES(:server_name, :server_ip, :server_port, :standard_test, :speedtest)
                    """)
            self.execute(sql, data)
            return self.return_message('Success !', 'Server added', 'success', True, True)
        else:
            return self.return_message('Error !', 'Regex error : Name (' + server_name + ') or IP (' + server_ip + ')',
                                       'error', True, True)

    def update_server(self, server_id, server_name, server_ip, server_port, standard_test, speedtest):
        if server_port != "":
            if not re.match(self.regex_port, server_port):
                return self.return_message('Error !', 'You can not update a server that does not exist', 'error', True,
                                           True)
        if re.match(self.regex_id, server_id) and re.match(self.regex_name, server_name) and re.match(self.regex_ip, server_ip):
            if self.get_range_server_from_id(server_id, server_id):
                data = {"server_id": server_id, "server_name": server_name, "server_ip": server_ip, "server_port": server_port, "standard_test": standard_test, "speedtest": speedtest}
                sql = ("""
                        UPDATE server SET
                        server_name=:server_name,
                        server_ip=:server_ip,
                        server_port=:server_port,
                        standard_test=:standard_test,
                        speedtest=:speedtest
                        WHERE id=:server_id
                        """)
                self.execute(sql, data)
                return self.return_message('Success !', 'Server updated', 'success', True, True)
            else:
                return self.return_message('Error !', 'You can not update a server that does not exist', 'error', True,
                                           True)
        else:
            return self.return_message('Error !', 'Regex error : ID (' + server_id + ') or Name (' + server_name
                                       + ') or IP (' + server_ip + ')', 'error', True, True)

    def delete_server(self, server_id):
        if re.match(self.regex_id, server_id):
            if self.get_range_server_from_id(server_id, server_id):
                data = {"server_id": server_id}
                sql = ("""
                        DELETE FROM server 
                        WHERE id=:server_id
                        """)
                self.execute(sql, data)
                return self.return_message('Success !', 'Server deleted', 'success', True, True)
            else:
                return self.return_message('Error !', 'You can not delete a server that does not exist', 'error', True,
                                           True)
        else:
            return self.return_message('Error !', 'Regex error : ID (' + server_id + ')', 'error', True, True)

    def get_all_server(self):
        data = {}
        sql = ("""
                SELECT * 
                FROM server
                """)
        self.execute(sql, data)
        return self.cursor.fetchall()

    def get_range_server_from_id(self, first_id, last_id):
        data = {"first_id": first_id, "last_id": last_id}
        sql = ("""
                SELECT * 
                FROM server
                WHERE id>=:first_id AND id<=:last_id
                """)
        self.execute(sql, data)
        return self.cursor.fetchone()

    def add_test(self, probe, standard_test_target, packet_number, packet_timeout, speedtest_target, speedtest_option, comment):
        if standard_test_target != "":
            if not re.match(self.regex_ip, standard_test_target):
                return 0
            if not 10 <= packet_number <= 300 and not 1 <= packet_timeout <= 100:
                return 0
        if speedtest_target["ip"] != "":
            if not re.match(self.regex_ip, speedtest_target["ip"]):
                return 0
            if not 1 <= speedtest_target["port"] <= 65535:
                return 0
        if standard_test_target == "" and speedtest_target["ip"] == "":
            return 0
        if not re.match(self.regex_comment, comment) or not 0 <= len(comment) <= 500:
            return 0

        if standard_test_target != "" and speedtest_target["ip"] != "":
            target = "Standard test -> " + standard_test_target + " - Speedtest ->" + speedtest_target["ip"] + ":" + str(speedtest_target["port"])
        elif speedtest_target["ip"] == "":
            target = "Standard test -> " + standard_test_target
        elif standard_test_target == "":
            target = "Speedtest ->" + speedtest_target["ip"] + ":" + str(speedtest_target["port"])

        data = {"date": datetime.now().replace(microsecond=0), "target": target, "probe": probe,
                "packet_number": packet_number, "packet_timeout": packet_timeout, "speedtest_option": speedtest_option,
                "comment": comment, "status": "waiting"}
        sql = ("""
                   INSERT INTO test(date, probe, target, packet_number, packet_timeout, speedtest_option, comment, status) 
                   VALUES(:date, :probe, :target, :packet_number, :packet_timeout, :speedtest_option, :comment, :status)
                   """)
        self.execute(sql, data)
        return self.cursor.lastrowid

    def update_test(self, type, test_id, data_to_update):
        if type == "user":
            if re.match(self.regex_id, test_id):
                if not re.match(self.regex_comment, data_to_update) or not 0 <= len(data_to_update) <= 500:
                    return self.return_message('Error !', 'Something wrent wrong',
                                               'error', True, True)
                if self.get_range_test_from_id(test_id, test_id):
                    data = {"test_id": test_id, "comment": data_to_update}
                    sql = ("""
                            UPDATE test SET
                            comment=:comment
                            WHERE id=:test_id
                            """)
                    self.execute(sql, data)
                    return self.return_message('Success !', 'Test updated', 'success', True, True)
                else:
                    return self.return_message('Error !', 'You can not delete a test that does not exist',
                                               'error', True, True)
            else:
                return self.return_message('Error !', 'Regex error : ID (' + test_id + ') or comments ('
                                           + data_to_update + ')', 'error', True, True)
        elif type == "probe":
            test_duration = (datetime.now().replace(microsecond=0) - datetime.strptime(self.get_range_test_from_id(data_to_update["id"], data_to_update["id"])["date"], '%Y-%m-%d %H:%M:%S'))
            data = {"id": data_to_update["id"], "test_duration": str(test_duration), "ping": data_to_update["ping"], "jitter": data_to_update["jitter"],
                    "packet_loss": data_to_update["packet_loss"], "mos": data_to_update["mos"], "download": data_to_update["download"],
                    "upload": data_to_update["upload"], "download_json_raw": data_to_update["download_json_raw"], "upload_json_raw": data_to_update["upload_json_raw"], "status": data_to_update["status"]}
            sql = ("""
                    UPDATE test SET
                    test_duration=:test_duration,
                    ping=:ping,
                    jitter=:jitter,
                    packet_loss=:packet_loss,
                    mos=:mos,
                    download=:download,
                    upload=:upload,
                    download_json_raw=:download_json_raw,
                    upload_json_raw=:upload_json_raw,
                    status=:status
                    WHERE id=:id
                    """)
            self.execute(sql, data)

    def delete_test(self, test_id):
        if re.match(self.regex_id, test_id):
            if self.get_range_test_from_id(test_id, test_id):
                data = {"test_id": test_id}
                sql = ("""
                        DELETE FROM test 
                        WHERE id=:test_id
                        """)
                self.execute(sql, data)
                return self.return_message('Success !', 'Test deleted', 'success', True, True)
            else:
                return self.return_message('Error !', 'You can not delete a test that does not exist', 'error', True,
                                           True)
        else:
            return self.return_message('Error !', 'Regex error : ID (' + test_id + ')', 'error', True, True)

    def get_all_test(self):
        data = {}
        sql = ("""
                SELECT * 
                FROM test
                ORDER BY
                id DESC
                """)
        self.execute(sql, data)
        return self.cursor.fetchall()

    def get_range_test_from_id(self, first_id, last_id):
        data = {"first_id": first_id, "last_id": last_id}
        sql = ("""
                SELECT * 
                FROM test
                WHERE id>=:first_id AND id<=:last_id
                """)
        self.execute(sql, data)
        return self.cursor.fetchone()

    def return_message(self, title, content, color, delete, container):
        session = {
            'title': title,
            'content': content,
            'color': self.template_config[color],
            'delete': delete,
            'container': container
        }
        return session, 1
