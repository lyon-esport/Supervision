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

import sys
import os
import json
import re
from pathlib import Path
from flask import Flask, session, redirect, request, render_template

# import local functions
from functions.Bdd import Bdd
from functions.session import get_message
from functions.Autotest import Autotest
from functions.ListServerZMQ import ListServerClientZMQ
from functions.ServerZMQ import ServerZMQREP
from functions.ClientZMQ import ClientZMQREQ


app = Flask(__name__)

# secret key to use session variable
app.secret_key = os.urandom(16)

# get templates configuration
with open('config/templates_config.json') as json_data_file:
    template_config = json.load(json_data_file)

# get server config
server_zmq_port = []
try:
    for port in range(0, int(os.environ.get("SERVER_ZMQ_NB_PORT", 0))):
        server_zmq_port.append(port + int(os.environ.get("SERVER_ZMQ_FIRST_PORT", 0)))
    server_config = {
        "server_zmq": {
            "port": server_zmq_port
        },

        "influxdb_url": str(os.environ.get("INFLUXDB_URL", ""))
    }
except Exception as error:
    print('Caught this error: ' + repr(error))
    sys.exit()
try:
    with open('config/server.json') as json_data_file:
        server_config.update(json.load(json_data_file))
except Exception as error:
    pass

# regex
regex_id = r"^[+]?[0-9]+$"
regex_ip = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
regex_port = r"^()([1-9]|[1-5]?[0-9]{2,4}|6[1-4][0-9]{3}|65[1-4][0-9]{2}|655[1-2][0-9]|6553[1-5])$"
regex_name = r"^[0-9a-zA-Z -_]{4,20}$"
regex_comment = r"^[a-zA-Z0-9@-_'\".()àéè&=+~^*!:?,<>ç{}%¨ ]*$"

# check if database is created
database_filename = "database.sqlite"
try:
    if not Path(database_filename).is_file():
        raise Exception('Please launch database_setup.py to create the database')
    bdd = Bdd(database_filename, template_config['color'], regex_id, regex_ip, regex_port, regex_name, regex_comment)
    bdd.connect()
    print("Connected to database %s" % database_filename)
except Exception as error:
    print('Caught this error: ' + repr(error))
    exit()

request_test_timeout = 120

# start server ZMQ
listServerZMQ = ListServerClientZMQ(bdd, server_config['influxdb_url'])
for i in range(0, len(set(server_config['server_zmq']['port']))):
    listServerZMQ.add("server", ServerZMQREP(server_config['server_zmq']['port'][i]))
    listServerZMQ.add("client", ClientZMQREQ(request_test_timeout))
    listServerZMQ.get("server", i).start()

listServerZMQ.start()

# create list for autotest
listAutotest = []


# URL redirection
@app.route('/index')
@app.route('/')
def index():
    return render_template(
                            'index.html',
                            active={'index': 'is-active'},
                            messages=get_message(),
                            clients=listServerZMQ.get_info_sondes(),
                            nbClientsAlive=listServerZMQ.get_nb_clients_alive(),
                            nbClientsAliveAndNotBusy=listServerZMQ.get_nb_clients_alive_and_not_busy(),
                            servers=bdd.get_all_server(),
                            influxdb_url=server_config['influxdb_url']
                           )


@app.route('/archive')
def archive():
    return render_template(
                            'archive.html',
                            active={'archive': 'is-active'},
                            messages=get_message(),
                            tests=bdd.get_all_test()
                           )


@app.route('/setting')
def setting():
    return render_template(
                            'setting.html',
                            active={'setting': 'is-active'},
                            messages=get_message(),
                            servers=bdd.get_all_server()
                           )


@app.route('/autotest')
def autotest():
    return render_template(
                            'autotest.html',
                            active={'autotest': 'is-active'},
                            messages=get_message(),
                            influxdb_url=server_config['influxdb_url'],
                            autotest=listAutotest
                           )


@app.route('/test', methods=['GET'])
def test():
    if request.method == 'GET':
        if bdd.get_range_test_from_id(request.values.get('id'), request.values.get('id')):
            test = bdd.get_range_test_from_id(request.values.get('id'), request.values.get('id'))
            speedtest_json = {}
            for speedtest in ["download_json_raw", "upload_json_raw"]:
                if test[speedtest]:
                    speedtest_json[speedtest] = json.dumps(json.loads(test[speedtest]), indent=2)
                else:
                    speedtest_json[speedtest] = ""
            return render_template(
                                    'test.html',
                                    active={'archive': 'is-active'},
                                    messages=get_message(),
                                    test=test,
                                    download_json_raw=speedtest_json["download_json_raw"],
                                    upload_json_raw=speedtest_json["upload_json_raw"]
                                   )
        else:
            session['message_0'] = {
                'title': 'Error !',
                'content': 'Test not found',
                'color': template_config['color']['error'],
                'delete': True,
                'container': True
            }
            session['nbMessage'] = 1
    return redirect('/archive')


@app.route('/backend_server', methods=['POST'])
def backend_server():
    if request.method == 'POST':
        if request.values.get('choice') == 'add_server':
            server_name = request.values.get('server_name')
            server_ip = request.values.get('server_ip')
            standard_test = "1" if request.values.get('standard_test') == "1" else "0"
            speedtest = "1" if request.values.get('speedtest') == "1" else "0"
            server_port = request.values.get('server_port') if speedtest == "1" else ""

            session['message_0'], session['nbMessage'] = bdd.add_server(server_name, server_ip, server_port, standard_test, speedtest)
        elif request.values.get('choice') == 'update_server':
            server_id = request.values.get('save_server_id')
            server_name = request.values.get('save_server_name')
            server_ip = request.values.get('save_server_ip')
            standard_test = "1" if request.values.get('save_standard_test') == "1" else "0"
            speedtest = "1" if request.values.get('save_speedtest') == "1" else "0"
            server_port = request.values.get('save_server_port') if speedtest == "1" else ""

            session['message_0'], session['nbMessage'] = bdd.update_server(server_id, server_name, server_ip, server_port, standard_test, speedtest)
        elif request.values.get('choice') == 'delete_server':
            server_id = request.values.get('server_id')
            session['message_0'], session['nbMessage'] = bdd.delete_server(server_id)
        else:
            session['message_0'] = {
                'title': 'Error !',
                'content': 'Page not found',
                'color': template_config['color']['error'],
                'delete': True,
                'container': True
            }
            session['nbMessage'] = 1
            return redirect('/')
    return redirect('/setting')


@app.route('/backend_autotest', methods=['POST'])
def backend_autotest():
    if request.method == 'POST':
        if request.values.get('choice') == 'delete_autotest':
            error_message = {
                'title': 'Error !',
                'content': 'Something wrent wrong',
                'color': template_config['color']['error'],
                'delete': True,
                'container': True
            }

            autotest_id = request.values.get('autotest_id')
            try:
                autotest_id = int(autotest_id)
                listAutotest[autotest_id].serverZMQ.client["autotest"] = False
                del listAutotest[autotest_id]
                session['message_0'] = {
                    'title': 'Success !',
                    'content': 'Autotest deleted !',
                    'color': template_config['color']['success'],
                    'delete': True,
                    'container': True
                }
                session['nbMessage'] = 1
                return redirect('/autotest')
            except Exception:
                session['message_0'] = error_message
                session['nbMessage'] = 1
                return redirect('/')
    session['message_0'] = {
        'title': 'Error !',
        'content': 'Page not found',
        'color': template_config['color']['error'],
        'delete': True,
        'container': True
    }
    session['nbMessage'] = 1
    return redirect('/')


@app.route('/backend_test', methods=['POST'])
def backend_test():
    if request.method == 'POST':
        if request.values.get('choice') == 'start':
            error_message = {
                    'title': 'Error !',
                    'content': 'Something wrent wrong',
                    'color': template_config['color']['error'],
                    'delete': True,
                    'container': True
                }
            standard_test = request.values.get('standard_test')
            speedtest = request.values.get('speedtest')
            autotest = request.values.get('autotest')

            if not standard_test == "True" and not speedtest == "True":
                session['message_0'] = error_message
                session['nbMessage'] = 1
                return redirect('/')

            if standard_test == "True":
                standard_test_target = request.values.get('standard_test_target')
                try:
                    packet_number = int(request.values.get('packet_number'))
                    packet_timeout = int(request.values.get('packet_timeout'))
                except Exception:
                    session['message_0'] = error_message
                    session['nbMessage'] = 1
                    return redirect('/')
                if standard_test_target == "other":
                    standard_test_target = request.values.get('standard_test_ip')
                if not re.match(regex_ip, standard_test_target):
                    session['message_0'] = error_message
                    session['nbMessage'] = 1
                    return redirect('/')
                if not 10 <= packet_number <= 300 or not 1 <= packet_timeout <= 5:
                    session['message_0'] = error_message
                    session['nbMessage'] = 1
                    return redirect('/')
            else:
                standard_test_target = ""
                packet_number = ""
                packet_timeout = ""
            if speedtest == "True":
                speedtest_choice = request.values.get('speedtest_choice')
                speedtest_target = request.values.get('speedtest_target')
                speedtest_option = request.values.get('speedtest_option')
                if speedtest_choice not in ["0", "1", "2"]:
                    session['message_0'] = error_message
                    session['nbMessage'] = 1
                    return redirect('/')
                if speedtest_target == "other":
                    try:
                        speedtest_target = {"ip": request.values.get('speedtest_ip'), "port": int(request.values.get('speedtest_port'))}
                    except Exception:
                        session['message_0'] = error_message
                        session['nbMessage'] = 1
                        return redirect('/')
                    if not re.match(regex_ip, speedtest_target["ip"]) or not 1 <= speedtest_target["port"] <= 65535:
                        session['message_0'] = error_message
                        session['nbMessage'] = 1
                        return redirect('/')
                else:
                    try:
                        speedtest_target = int(speedtest_target)
                        result = bdd.get_range_server_from_id(speedtest_target, speedtest_target)
                        speedtest_target = {"ip": result["server_ip"], "port": result["server_port"]}
                    except Exception:
                        session['message_0'] = error_message
                        session['nbMessage'] = 1
                        return redirect('/')
            else:
                speedtest_choice = ""
                speedtest_target = {"ip": "", "port": ""}
                speedtest_option = ""

            if autotest == "True":
                autotest_timer = request.values.get('autotest_timer')
            else:
                autotest_timer = 0
            try:
                autotest_timer = int(autotest_timer)
                probe_int = int(request.values.get('probe'))
                probe = listServerZMQ.get("server", probe_int)
            except Exception:
                session['message_0'] = error_message
                session['nbMessage'] = 1
                return redirect('/')

            if not probe.is_alive() or probe.client["busy"]:
                session['message_0'] = error_message
                session['nbMessage'] = 1
                return redirect('/')
            comment = request.values.get('comments')
            if not re.match(regex_comment, comment) or not 0 <= len(comment) <= 500:
                session['message_0'] = error_message
                session['nbMessage'] = 1
                return redirect('/')
            if server_config['influxdb_url']:
                autotest == "False"
            if autotest == "True":
                if probe.client["autotest"]:
                    session['message_0'] = error_message
                    session['nbMessage'] = 1
                    return redirect('/')
                else:
                    listAutotest.append(
                                        Autotest(probe, listServerZMQ.get("client", probe_int), autotest_timer, standard_test_target, packet_number, packet_timeout, speedtest_choice, speedtest_target, speedtest_option, comment)
                                        )
                    listAutotest[-1].start()
                return redirect('/autotest')
            else:
                test_id = bdd.add_test(probe.client["name"], standard_test_target, packet_number, packet_timeout, speedtest_target, speedtest_option, comment)
                listServerZMQ.get("client", probe_int).start_test(probe.client["address"], probe.client["port"],
                                                                  {
                                                                   "type": "test",
                                                                   "id": test_id,
                                                                   "probe_name": probe.client["name"],
                                                                   "standard_test_target": standard_test_target,
                                                                   "packet_number": packet_number,
                                                                   "packet_timeout": packet_timeout,
                                                                   "speedtest_choice": speedtest_choice,
                                                                   "speedtest_target": speedtest_target,
                                                                   "speedtest_option": speedtest_option,
                                                                   "comment": comment,
                                                                   "influxdb": False
                                                                   }
                                                                  )
                return redirect('/test?id=' + str(test_id))
        elif request.values.get('choice') == 'update_test':
            test_id = request.values.get('test_id')
            comment = request.values.get('comments')
            if not re.match(regex_comment, comment) or not 0 <= len(comment) <= 500:
                session['message_0'] = {
                    'title': 'Error !',
                    'content': 'Something wrent wrong',
                    'color': template_config['color']['error'],
                    'delete': True,
                    'container': True
                }
                session['nbMessage'] = 1
                return redirect('/archive')
            session['message_0'], session['nbMessage'] = bdd.update_test("user", test_id, comment)
            return redirect('/test?id=' + test_id)
        elif request.values.get('choice') == 'delete_test':
            test_id = request.values.get('test_id')
            if not bdd.get_range_test_from_id(test_id, test_id) or bdd.get_range_test_from_id(test_id, test_id)["status"] == "waiting":
                session['message_0'] = {
                    'title': 'Error !',
                    'content': 'You can\'t delete a test in waiting',
                    'color': template_config['color']['error'],
                    'delete': True,
                    'container': True
                }
                session['nbMessage'] = 1
            else:
                session['message_0'], session['nbMessage'] = bdd.delete_test(test_id)
        else:
            session['message_0'] = {
                'title': 'Error !',
                'content': 'Page not found',
                'color': template_config['color']['error'],
                'delete': True,
                'container': True
            }
            session['nbMessage'] = 1
    return redirect('/archive')


@app.route('/api', methods=['GET'])
def api():
    if request.method == 'GET':
        if request.values.get('sonde_info') == '1':
            return render_template(
                                    'info_probe.html',
                                    clients=listServerZMQ.get_info_sondes(),
                                    nbClientsAlive=listServerZMQ.get_nb_clients_alive(),
                                   )
        elif request.values.get('sonde_select') == '1':
            return render_template(
                                        'select_probe.html',
                                        clients=listServerZMQ.get_info_sondes(),
                                        nbClientsAlive=listServerZMQ.get_nb_clients_alive(),
                                        nbClientsAliveAndNotBusy=listServerZMQ.get_nb_clients_alive_and_not_busy()
                                    )
        elif request.values.get('test_info') == '1':
            test = bdd.get_range_test_from_id(request.values.get('id'), request.values.get('id'))
            speedtest_json = {}
            for speedtest in ["download_json_raw", "upload_json_raw"]:
                if test[speedtest]:
                    speedtest_json[speedtest] = json.dumps(json.loads(test[speedtest]), indent=2)
                else:
                    speedtest_json[speedtest] = ""
            return render_template(
                                    'info_test.html',
                                    test=test,
                                    download_json_raw=speedtest_json["download_json_raw"],
                                    upload_json_raw=speedtest_json["upload_json_raw"]
                                    )
        else:
            session['message_0'] = {
                'title': 'Error !',
                'content': 'Page not found',
                'color': template_config['color']['error'],
                'delete': True,
                'container': True
            }
            session['nbMessage'] = 1
    return redirect('/')


# HTTP 404
@app.errorhandler(404)
def page_not_found(e):
    session['message_0'] = {
                            'title': 'Error 404 !', 
                            'content': 'Page not found',
                            'color': template_config['color']['error'],
                            'delete': True,
                            'container': True
                            }
    session['nbMessage'] = 1
    return redirect('/')
