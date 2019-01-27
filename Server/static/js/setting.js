// ----------------------------------------------------------------------------
// Copyright © Lyon e-Sport, 2018
//
// Contributeur(s):
//     * Ortega Ludovic - ludovic.ortega@lyon-esport.fr
//     * Etienne Guilluy - etienne.guilluy@lyon-esport.fr
//     * Barbou Théo - theobarbou@gmail.com
//     * Dupessy Clément - clement07131@hotmail.fr
//     * Julian Marty - julian.marty83@gmail.com
//
// Ce logiciel, Supervision, est un programme informatique servant à lancer des tests réseaux
// (ping/jitter/packet loss/mos/download/upload) sur des sondes via un site web.
//
// Ce logiciel est régi par la licence CeCILL soumise au droit français et
// respectant les principes de diffusion des logiciels libres. Vous pouvez
// utiliser, modifier et/ou redistribuer ce programme sous les conditions
// de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
// sur le site "http://www.cecill.info".
//
// En contrepartie de l'accessibilité au code source et des droits de copie,
// de modification et de redistribution accordés par cette licence, il n'est
// offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
// seule une responsabilité restreinte pèse sur l'auteur du programme,  le
// titulaire des droits patrimoniaux et les concédants successifs.
//
// A cet égard  l'attention de l'utilisateur est attirée sur les risques
// associés au chargement,  à l'utilisation,  à la modification et/ou au
// développement et à la reproduction du logiciel par l'utilisateur étant
// donné sa spécificité de logiciel libre, qui peut le rendre complexe à
// manipuler et qui le réserve donc à des développeurs et des professionnels
// avertis possédant  des  connaissances  informatiques approfondies.  Les
// utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
// logiciel à leurs besoins dans des conditions permettant d'assurer la
// sécurité de leurs systèmes et ou de leurs données et, plus généralement,
// à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.
//
// Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
// pris connaissance de la licence CeCILL, et que vous en avez accepté les
// termes.
// ----------------------------------------------------------------------------

'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const regexIP = new RegExp("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$");
    const regexName = new RegExp("^[0-9a-zA-Z -_]{4,20}$");
    const regexPort = new RegExp("^()([1-9]|[1-5]?[0-9]{2,4}|6[1-4][0-9]{3}|65[1-4][0-9]{2}|655[1-2][0-9]|6553[1-5])$");

    let checkFieldNewServer = [];

    let checkFieldEditServer = [];

    createEventListenerForEdit();

    document.getElementById("server_name").addEventListener("input", function () {
        checkFieldNewServer['server_name'] = checkInputText("server_name", 4, 20, regexName);
        disableForm(checkFieldNewServer, 'button_add_server');
    }, {passive: true});

    document.getElementById("server_ip").addEventListener("input", function () {
        checkFieldNewServer['server_ip'] = checkRegex("server_ip", regexIP);
        disableForm(checkFieldNewServer, 'button_add_server');
    }, {passive: true});

    document.getElementById("server_port").addEventListener("input", function () {
        checkFieldNewServer['server_port'] = checkRegex("server_port", regexPort);
        if(document.getElementById("speedtest").checked===false)
        {
            checkFieldNewServer['server_port'] = true;
        }
        disableForm(checkFieldNewServer, 'button_add_server');
    }, {passive: true});

    document.getElementById("speedtest").addEventListener("change", function () {
        checkFieldNewServer['test'] = document.getElementById("speedtest").checked===true || document.getElementById("standard_test").checked===true;
        document.getElementById("speedtest").checked===true ? document.getElementById("field_server_port").classList.remove("is-hidden") : document.getElementById("field_server_port").classList.add("is-hidden");
        document.getElementById("server_port").dispatchEvent(new Event("input"));
    }, {passive: true});

    document.getElementById("standard_test").addEventListener("change", function () {
        checkFieldNewServer['test'] = document.getElementById("speedtest").checked===true || document.getElementById("standard_test").checked===true;
        disableForm(checkFieldNewServer, 'button_add_server');
    }, {passive: true});

    document.getElementById("server_name").dispatchEvent(new Event("input"));
    document.getElementById("server_ip").dispatchEvent(new Event("input"));
    document.getElementById("server_port").dispatchEvent(new Event("input"));
    document.getElementById("speedtest").dispatchEvent(new Event("change"));
    document.getElementById("standard_test").dispatchEvent(new Event("change"));
    disableForm(checkFieldNewServer, 'button_add_server');

    document.getElementById("save_server_name").addEventListener("input", function () {
        checkFieldEditServer['save_server_name'] = checkInputText("save_server_name", 4, 20, regexName);
        disableForm(checkFieldEditServer, 'button_save_server');
    }, {passive: true});

    document.getElementById("save_server_ip").addEventListener("input", function () {
        checkFieldEditServer['save_server_ip'] = checkRegex("save_server_ip", regexIP);
        disableForm(checkFieldEditServer, 'button_save_server');
    }, {passive: true});

    document.getElementById("save_server_port").addEventListener("input", function () {
        checkFieldEditServer['save_server_port'] = checkRegex("save_server_port", regexPort);
        if(document.getElementById("save_speedtest").checked===false)
        {
            checkFieldEditServer['save_server_port'] = true;
        }
        disableForm(checkFieldEditServer, 'button_save_server');
    }, {passive: true});

    document.getElementById("save_speedtest").addEventListener("change", function () {
        checkFieldEditServer['save_test'] = document.getElementById("save_speedtest").checked===true || document.getElementById("save_standard_test").checked===true;
        document.getElementById("save_speedtest").checked===true ? document.getElementById("field_save_server_port").classList.remove("is-hidden") : document.getElementById("field_save_server_port").classList.add("is-hidden");
        document.getElementById("save_server_port").dispatchEvent(new Event("input"));
    }, {passive: true});

    document.getElementById("save_standard_test").addEventListener("change", function () {
        checkFieldEditServer['save_test'] = document.getElementById("save_speedtest").checked===true || document.getElementById("save_standard_test").checked===true;
        disableForm(checkFieldEditServer, 'button_save_server');
    }, {passive: true});

    document.getElementById("save_server_name").dispatchEvent(new Event("input"));
    document.getElementById("save_server_ip").dispatchEvent(new Event("input"));
    document.getElementById("save_server_port").dispatchEvent(new Event("input"));
    document.getElementById("save_speedtest").dispatchEvent(new Event("change"));
    document.getElementById("save_standard_test").dispatchEvent(new Event("change"));
    disableForm(checkFieldEditServer, 'button_save_server');

    document.getElementById("button_cancel_save_server").addEventListener("click", function () {
        document.getElementById("form_edit").classList.add("is-hidden");
    }, {passive: true});

    function checkInputText(id, min_length, max_length, regex)
    {
        let inputObject = document.getElementById(id);
        let favIconObject = document.getElementById(id).nextElementSibling.children[0];

        if(inputObject.value.length >= min_length && inputObject.value.length <= max_length && regex.test(inputObject.value))
        {
            inputObject.classList.add("is-success");
            inputObject.classList.remove("is-danger");

            favIconObject.classList.add("fa-check");
            favIconObject.classList.remove("fa-exclamation-triangle");

            return true;
        }
        else
        {
            inputObject.classList.add("is-danger");
            inputObject.classList.remove("is-success");

            favIconObject.classList.add("fa-exclamation-triangle");
            favIconObject.classList.remove("fa-check");

            return false;
        }
    }

    function checkRegex(id, regex)
    {
        let inputObject = document.getElementById(id);
        let favIconObject = document.getElementById(id).nextElementSibling.children[0];

        if(regex.test(inputObject.value))
        {
            inputObject.classList.add("is-success");
            inputObject.classList.remove("is-danger");

            favIconObject.classList.add("fa-check");
            favIconObject.classList.remove("fa-exclamation-triangle");

            return true;
        }
        else
        {
            inputObject.classList.add("is-danger");
            inputObject.classList.remove("is-success");

            favIconObject.classList.add("fa-exclamation-triangle");
            favIconObject.classList.remove("fa-check");

            return false;
        }
    }

    function disableForm(checkField, id)
    {
        let buttonSendForm = document.getElementById(id);

        for(let key in checkField)
        {
            if(checkField[key]===false)
            {
                buttonSendForm.setAttribute("disabled", "disabled");
                return 0;
            }
            else
            {
                buttonSendForm.removeAttribute("disabled");
            }
        }
    }

    function createEventListenerForEdit()
    {
        let listEditButton = document.getElementsByClassName("edit_server");

        for(let i=0; i< listEditButton.length; i++)
        {
            if(typeof listEditButton[i] !== 'undefined')
            {
                document.getElementById("button_edit_server_" + listEditButton[i].getAttribute("aria-server_id")).addEventListener("click", function () {
                    document.getElementById("save_server_id").value = listEditButton[i].getAttribute("aria-server_id");
                    document.getElementById("form_edit").classList.remove("is-hidden");
                    document.getElementById("save_server_name").value = listEditButton[i].getAttribute("aria-server_name");
                    document.getElementById("save_server_name").dispatchEvent(new Event('input'));
                    document.getElementById("save_server_ip").value = listEditButton[i].getAttribute("aria-server_ip");
                    document.getElementById("save_server_ip").dispatchEvent(new Event('input'));
                    listEditButton[i].getAttribute("aria-standard_test") === "1" ? document.getElementById("save_standard_test").checked = true : document.getElementById("save_standard_test").checked = false;
                    if(listEditButton[i].getAttribute("aria-speedtest") === "1")
                    {
                        document.getElementById("save_speedtest").checked = true;
                        document.getElementById("field_save_server_port").classList.remove("is-hidden");
                        document.getElementById("save_server_port").value = listEditButton[i].getAttribute("aria-server_port");
                        document.getElementById("save_server_port").dispatchEvent(new Event('input'));
                    }
                    else
                    {
                        document.getElementById("save_speedtest").checked = false;
                        document.getElementById("field_save_server_port").classList.add("is-hidden");
                        document.getElementById("save_server_port").dispatchEvent(new Event('input'));
                    }
                    document.getElementById("save_standard_test").dispatchEvent(new Event('change'));
                    document.getElementById("save_speedtest").dispatchEvent(new Event('change'));
                }, {passive: true});
            }
        }
    }
});