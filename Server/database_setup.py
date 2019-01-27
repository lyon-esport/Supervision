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

import sqlite3
from pathlib import Path

if not Path("database.sqlite").is_file():
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()

    # Create table server
    c.execute('''CREATE TABLE IF NOT EXISTS server(
                id INTEGER         PRIMARY KEY AUTOINCREMENT,
                server_name VARCHAR( 255 ), 
                server_ip VARCHAR( 255 ),
                server_port INTEGER,
                standard_test INTEGER, 
                speedtest INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS test(
                    id INTEGER         PRIMARY KEY AUTOINCREMENT, 
                    date VARCHAR( 255 ),
                    test_duration VARCHAR( 255 ),
                    probe VARCHAR( 255 ),
                    target VARCHAR( 255 ),
                    packet_number VARCHAR( 255 ),
                    packet_timeout VARCHAR( 255 ),
                    ping VARCHAR( 255 ),
                    jitter VARCHAR( 255 ),
                    packet_loss VARCHAR( 255 ),
                    mos VARCHAR( 255 ),
                    download VARCHAR( 255 ),
                    download_json_raw VARCHAR( 5000 ),
                    upload VARCHAR( 255 ),
                    upload_json_raw VARCHAR( 5000 ),
                    speedtest_option VARCHAR( 255 ),
                    comment VARCHAR( 1000 ),
                    status VARCHAR( 255 )
                    )''')

    conn.commit()
    conn.close()
else:
    print("Database already created")
