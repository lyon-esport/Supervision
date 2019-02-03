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

import json, os, sys, socket, struct, select, time, getopt, subprocess


ICMP_ECHO_REQUEST = 8 # ICMP de type 8 -> Echo Request


def checksum(source_string):
    sum = 0
    max_count = (len(source_string)/2)*2
    count = 0
    while count < max_count:
        val = source_string[count + 1]*256 + source_string[count]                       

        sum = sum + val
        sum = sum & 0xffffffff 
        count = count + 2
 
    if max_count < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff 
 
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receive_one_ping(sock, ID, timeout):
    """
    Reçoit un ping du socket.
    """
    time_remaining = timeout
    while True:
        start_time = time.time()
        readable = select.select([sock], [], [], time_remaining)
        time_spent = (time.time() - start_time)
        if readable[0] == []: # Timeout
            return
 
        time_received = time.time()
        recv_packet, addr = sock.recvfrom(1024)
        icmp_header = recv_packet[20:28]
        type, code, checksum, packet_ID, sequence = struct.unpack(
            "bbHHh", icmp_header
        )
        if packet_ID == ID:
            bytes_In_double = struct.calcsize("d")
            time_sent = struct.unpack("d", recv_packet[28:28 + bytes_In_double])[0]
            return time_received - time_sent
 
        time_remaining = time_remaining - time_spent
        if time_remaining <= 0:
            return

        
def send_one_ping(my_socket, dest_addr, ID):
    """
    Envoi un ping à l'adresse donné.
    """
    dest_addr = socket.gethostbyname(dest_addr)
    
    my_checksum = 0

    # Make a dummy header with a 0 checksum.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + bytes(data.encode('utf-8'))  # CHangement d'octets

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))


def do_one(src_addr, dest_addr, timeout):
    """
    Renvoie soit la latence, soit rien si le paquet a un timeout
    """
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error as e:
        if e.errno == 1:
            # Opération non permise
            e.msg = e.msg + (
                " - Veuillez noter que les ICMP peuvent être envoyés uniquement depuis l'utilisateur root"
            )
            raise socket.error(e.msg)
        raise # raise the original error

    my_ID = os.getpid() & 0xFFFF

    my_socket.bind((src_addr,0))

    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return delay


def verbose_ping(src_addr, dest_addr, timeout=2, count=4):
    """
    Send >count< ping to >dest_addr< with the given >timeout< and display
    the result.
    Envoie 'count' ping vers 'dest_addr' with le 'timeout' donné, puis affiche
    """
    for i in range(count):
        print("ping %s..." % dest_addr,)
        try:
            delay = do_one(src_addr, dest_addr, timeout)
        except socket.gaierror as e:
            print ("failed. (socket error: '%s')" % e[1])
            break

        if delay is None:
            print("failed. (timeout within %ssec.)" % timeout)
        else:
            delay = delay * 1000
            print("get ping in %0.4fms" % delay)


def start_standard_test(count, timeout, src_addr, src_name, dest_addr, dest_name, output, rrd_file):
    '''
    TEST
    response = os.system("ping " + dest_addr)
    if response != 0:
        result_speedtest = speedtest(dest_addr)
        host_unreachable = "host unreachable"
        return host_unreachable, host_unreachable, host_unreachable, result_speedtest, host_unreachable
    '''
    lost = 0        # Nombre de paquet perdu
    mos = 0         # Score d'opinion moyen 
    latency = []    # Valeur de latence [MIN,MOY,MAX]
    jitter = []     # Valeur de gigue [MAX,MOY]
    time_sent = []  # Horaire du paquet envoyé
    time_recv = []  # Horaire du paquet reçu

    # On catch les erreurs du module getopt
    help_line = 'Usage: %s -c [count] -t [timeout] -a [srcname] -b [dstname] -s [srcip] -d [dsthost] ' \
                '-o [normal|nagios|rrd] -f [rrd file]'

    opts, args = getopt.getopt(sys.argv[1:], ':hc:t:a:b:s:d:o:f:')
    for opt, arg in opts:
        if opt in '-h':
            raise Exception("ERROR: " + help_line % sys.argv[0])
        if opt in '-c':
            count = int(arg)
        elif opt in '-t':
            timeout = int(arg)
        elif opt in '-s':
            src_addr = arg
            if 'src' == src_name:
                src_name = src_addr
        elif opt in '-a':
            src_name = arg
        elif opt in '-d':
            dest_addr = arg
            if 'dst' == dest_name:
                dest_name = dest_addr
        elif opt in '-b':
            dest_name = arg
        elif opt in '-o':
            output = arg
        elif opt in '-f':
            rrd_file = arg

    # On vérifie qu'on envoie bien au moins 1 paquet
    if count <= 0:
        raise Exception("ERROR: count must be greater than zero.")

    # On vérifie qu'on tolère un timeout d'au moins 1 seconde
    if timeout <= 0:
        raise Exception("ERROR: timeout must be greater than zero.")
        
    for i in range(0, count):
        time_sent.append(int(round(time.time() * 1000)))
        d = do_one(src_addr, dest_addr, timeout)
        if d is None:
            lost = lost + 1
            time_recv.append(None)
        else:
            time_recv.append(int(round(time.time() * 1000)))
        # Calcul de la latence
        latency.append(time_recv[i] - time_sent[i])

        # Calculer la Gigue avec la paquet précédent 
        # http://toncar.cz/Tutorials/VoIP/VoIP_Basics_Jitter.html
        if len(jitter) == 0:
            # Premier paquet reçu, Gigue = 0
            jitter.append(0)
        else:
            # Trouver le paquet précédent: 
            for h in reversed(range(0, i)):
                if time_recv[h] != None:
                    break
            # Calcul de la différence relative des temps de transit
            drtt = (time_recv[i] - time_recv[h]) - (time_sent[i] - time_sent[h])
            jitter.append(jitter[len(jitter) - 1] + (abs(drtt) - jitter[len(jitter) - 1]) / float(16))

    # Calcul du score d'opinion moyen
    if len(latency) > 0:
        EffectiveLatency = (sum(latency) / (len(latency) + max(jitter) * 2 + 10))
        if EffectiveLatency < 160:
           R = 93.2 - (EffectiveLatency / 40)
        else:
            R = 93.2 - (EffectiveLatency - 120) / 10
            # Nous soustrayons 2.5 R par pourcentage de paquet perdu 
            R = R - (lost * 2.5)
            # Converti le R en valeur MOS
        mos = (1 + 0.035 * R + .000007 * R * (R-60) * (100-R))

    # Mise en place des valeurs (timeout, paquets perdus, et mos déjà calculé)
    lost_perc = lost / float(count) * 100
    if len(latency) > 0:
        min_latency = min(latency)
        max_latency = max(latency)
        avg_latency = sum(latency) / len(latency)
    else:
        min_latency = 'NaN'
        max_latency = 'NaN'
        avg_latency = 'NaN'
    if len(jitter) != 0:
        tot_jitter = jitter[len(jitter) - 1]
    else:
        tot_jitter = 'NaN'

    # Affichage des valeurs
    if output == 'default':
        print("Statistics for %s to %s:" % (src_name, dest_name))
        print(" - packet loss: %i (%.2f%%)" % (lost, lost_perc))
        if type(min_latency) != str and type(max_latency) != str and type(avg_latency) != str:
            print(" - latency (MIN/MAX/AVG): %i/%i/%i" % (min_latency, max_latency, avg_latency))
        else:
            print(" - latency (MIN/MAX/AVG): %s/%s/%s" % (min_latency, max_latency, avg_latency))
        if type(tot_jitter) != str:
            print(" - jitter: %.4f" % tot_jitter)
        else:
            print(" - jitter: %s" % tot_jitter)
        print(" - MOS: %.1f" % mos)
    elif output == 'return':
        result_ping = {"min": min_latency, "max": max_latency, "avg": avg_latency}
        result_jitter = "%.2f" % tot_jitter
        result_packet_loss = {"packet_number": lost, "packet_percent": lost_perc}
        result_mos = "%.2f" % mos
        return result_ping, result_jitter, result_packet_loss, result_mos

    else:
        raise Exception("ERROR: output not defined.")


def start_speedtest(type, address, port, arg):

    test_result = {}

    if type == "0":
        options = {"download": "-R " + arg, "upload": arg}
    elif type == "1":
        options = {"download": "-R " + arg}
        test_result["upload"] = ""
    elif type == "2":
        options = {"upload": arg}
        test_result["download"] = ""

    for key in options:
        try:
            if os.name == "nt":
                proc = subprocess.Popen(("iperf3" + " -c " + address + " -p " + port + " -J " + options[key]), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                proc = subprocess.Popen(["iperf3", " -c ", address, " -p ", port, " -J ", options[key]], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = json.loads(proc.communicate()[0].decode())
            if "error" not in result:

                bits_per_second_min = None
                bits_per_second_max = None
                nb_bits = 0

                for interval in result["intervals"]:
                    for streams in result["intervals"][0]["streams"]:
                        bits_per_second = (interval["streams"][0]["bits_per_second"])
                        nb_bits = nb_bits + bits_per_second
                        if bits_per_second_min is None or bits_per_second_min > bits_per_second:
                            bits_per_second_min = bits_per_second
                        if bits_per_second_max is None or bits_per_second_max < bits_per_second:
                            bits_per_second_max = bits_per_second

                speedtest_min = bits_per_second_min
                speedtest_avg = nb_bits / (result["end"]["streams"][0]["sender"]["seconds"]) / len(
                    result["intervals"][0]["streams"])
                speedtest_max = bits_per_second_max

                test_result[key] = {"status": "success", "result": {"min": int(speedtest_min), "avg": int(speedtest_avg), "max": int(speedtest_max)},
                                    "json": json.dumps(result)}
            else:
                test_result[key] = {"status": "error", "message": result["error"], "json": json.dumps(result)}
            time.sleep(5)
        except FileNotFoundError:
            test_result[key] = {"status": "error", "message": "iperf3 not detected"}
        except Exception:
            test_result[key] = {"status": "error", "message": "bad syntax commands option"}

    return test_result
