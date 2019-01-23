// ----------------------------------------------------------------------------
// Copyright © Lyon e-Sport, 2018
//
// Contributeur(s):
//     * Ortega Ludovic - ludovic.ortega@lyon-esport.fr
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

const regexIP = new RegExp("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$");
const regexComment = new RegExp("^[a-zA-Z0-9@-_'\".()àéè&=+~^*!:?,<>ç{}%¨ ]*$");

const radioButtons = {
    "standard_test":{
        "subClass": ["", "no_"],
        "options":["field_packet_number", "field_packet_timeout"],
        "son_event": "change"
    },
    "speedtest":{
        "subClass": ["", "no_"],
        "options":[],
        "son_event": "change"
    },
    "autotest":{
        "subClass": ["", "no_"],
        "options":[],
        "son_event": "input"
    }
};

const selectTarget = {
    "standard_test_target":{
        "options":["standard_test_target_ip"]
    },
    "speedtest_target":{
        "options":["speedtest_target_ip", "speedtest_target_port"]
    }
};

const input = {
    "int": {
        "packet_number": {
            "Min": 10,
            "Max": 300
        },
        "packet_timeout": {
            "Min": 1,
            "Max": 5
        },
        "speedtest_port": {
            "Min": 1,
            "Max": 65535
        },
        "autotest_target": {
            "Min": 10,
            "Max": 300
        }
    },
    "ip": [
        "standard_test_ip",
        "speedtest_ip"
    ],
    "comment": [
        "comments"
    ]
};

document.addEventListener('DOMContentLoaded', () => {

    setInterval(get_sonde_info,1000);

    createInputTargetEvent();
    createTargetEvent();
    createRadioEvent();

    document.getElementById("standard_test").dispatchEvent(new Event("change"));
    document.getElementById("speedtest").dispatchEvent(new Event("change"));
    document.getElementById("probe_select_refresh").addEventListener("click", function () {
        get_sonde_select()
    }, {passive: true});
    if(document.getElementById("autotest"))
    {
        document.getElementById("autotest").dispatchEvent(new Event("change"));
    }
    document.getElementById("comments").dispatchEvent(new Event("keyup"));
});

function get_sonde_info()
{
    fetch('/api?sonde_info=1').then(function(response) {
        return (response.text());
    })
    .then(function(responseText)
    {
        if(document.getElementById("probe_info").innerHTML !== responseText)
        {
            document.getElementById("probe_info").innerHTML = responseText;
        }
    })
    .catch(function(error)
    {
        console.log('Fetch API error: ' + error.message);
        document.getElementById("probe_info").innerHTML = "<article class=\"message is-danger\"><div class=\"message-header\"><p>Error !</p></div><div class=\"message-body\"><span class=\"has-text-danger\"><span class=\"icon\"><i class=\"fas fa-ban\" aria-hidden=\"true\"></i></span>" + "Fetch API Error: " + error.message + "</span></div></article>";
    });
}

function get_sonde_select()
{
    fetch('/api?sonde_select=1').then(function(response) {
        return (response.text());
    })
    .then(function(responseText)
    {
        if(document.getElementById("probe_select").innerHTML !== responseText)
        {
            document.getElementById("probe_select").innerHTML = responseText;
        }
        disableForm();
    })
    .catch(function(error)
    {
        console.log('Fetch API error: ' + error.message);
        document.getElementById("probe_select").innerHTML = "<div class=\"field-body\"><div class=\"field\"><span class=\"has-text-danger has-text-weight-bold\"><span class=\"icon\"><i class=\"fas fa-ban\" aria-hidden=\"true\"></i></span>Fetch API Error: " + error.message + "&nbsp</span></div></div>";
        document.getElementById("start_test").setAttribute("disabled", "disabled");
    });


}

function createRadioEvent()
{
    for(let index in radioButtons)
    {
        for(let indexSubClass in radioButtons[index]["subClass"])
        {
            if(document.getElementById(radioButtons[index]["subClass"][indexSubClass] + index))
            {
                document.getElementById(radioButtons[index]["subClass"][indexSubClass] + index).addEventListener("change", function () {
                    document.getElementById(index).checked === true ? document.getElementById("field_" + index + "_target").classList.remove("is-hidden") : document.getElementById("field_" + index + "_target").classList.add("is-hidden");

                    for (let indexOptions in radioButtons[index]["options"]) {
                        document.getElementById(index).checked === true ? document.getElementById(radioButtons[index]["options"][indexOptions]).classList.remove("is-hidden") : document.getElementById(radioButtons[index]["options"][indexOptions]).classList.add("is-hidden");
                        document.getElementById(radioButtons[index]["options"][indexOptions]).children[1].children[0].children[0].dispatchEvent(new Event("input"));
                    }
                    document.getElementById(index + "_target").dispatchEvent(new Event(radioButtons[index]["son_event"]));
                    disableForm();
                }, {passive: true});
            }
        }
    }
}

function createTargetEvent()
{
    for(let index in selectTarget)
    {
        document.getElementById(index).addEventListener("change", function () {
            for(let indexOptions in selectTarget[index]["options"])
            {
                document.getElementById(index).value === "other" ? document.getElementById(selectTarget[index]["options"][indexOptions]).classList.remove("is-hidden") : document.getElementById(selectTarget[index]["options"][indexOptions]).classList.add("is-hidden");
                document.getElementById(selectTarget[index]["options"][indexOptions]).children[0].dispatchEvent(new Event("input"));
            }
            disableForm();
        }, {passive: true});
    }
}

function createInputTargetEvent()
{
    for(let subIndex in input["int"])
    {
        if(document.getElementById(subIndex))
        {
            document.getElementById(subIndex).addEventListener("input", function () {
                let state = document.getElementById(subIndex).value >= input["int"][subIndex]["Min"] && document.getElementById(subIndex).value <= input["int"][subIndex]["Max"];
                displayInputValidation(subIndex, state);
                disableForm();
            }, {passive: true});
        }
    }
    for(let subIndex in input["ip"])
    {
        if(document.getElementById(input["ip"][subIndex]))
        {
            document.getElementById(input["ip"][subIndex]).addEventListener("input", function () {
                let state = regexIP.test(document.getElementById(input["ip"][subIndex]).value);
                displayInputValidation(input["ip"][subIndex], state);
                disableForm();
            }, {passive: true});
        }
    }

    for(let subIndex in input["comment"])
    {
        if(document.getElementById(input["ip"][subIndex]))
        {
            document.getElementById(input["comment"][subIndex]).addEventListener("keyup", function () {
                checkInputComment(input["comment"][subIndex], 0, 500, regexComment);
                disableForm();
            }, {passive: true});
        }
    }
}

function displayInputValidation(id, state)
{
    let inputObject = document.getElementById(id);
    let favIconObject = document.getElementById(id).nextElementSibling.children[0];

    if(state)
    {
        inputObject.classList.add("is-success");
        inputObject.classList.remove("is-danger");

        favIconObject.classList.add("fa-check");
        favIconObject.classList.remove("fa-exclamation-triangle");
    }
    else
    {
        inputObject.classList.add("is-danger");
        inputObject.classList.remove("is-success");

        favIconObject.classList.add("fa-exclamation-triangle");
        favIconObject.classList.remove("fa-check");
    }
}

function checkInputComment(id, min_length, max_length, regex)
{
    let inputObject = document.getElementById(id);

    if(inputObject.value.length >= min_length && inputObject.value.length <= max_length && regex.test(inputObject.value))
    {
        inputObject.classList.add("is-success");
        inputObject.classList.remove("is-danger");

        return true;
    }
    else
    {
        inputObject.classList.add("is-danger");
        inputObject.classList.remove("is-success");

        return false;
    }
}

function disableForm()
{
    let oneRadioChecked = document.getElementById("standard_test").checked===true || document.getElementById("speedtest").checked===true;

    let standard_test_ip = true;
    let packetNumber = true;
    let packetTimeout = true;

    let speedtest_ip = true;
    let speedtest_port = true;

    let probeFree = document.getElementById("probe_select").children[0].classList.contains('select');
    console.log("Test" + probeFree);
    let autotest = true;

    let comments = checkInputComment("comments", 0, 500, regexComment);

    if(document.getElementById("standard_test").checked===true)
    {
        packetNumber = document.getElementById("packet_number").value >= input["int"]["packet_number"]["Min"] && document.getElementById("packet_number").value <= input["int"]["packet_number"]["Max"];
        packetTimeout = document.getElementById("packet_timeout").value >= input["int"]["packet_timeout"]["Min"] && document.getElementById("packet_timeout").value <= input["int"]["packet_timeout"]["Max"];
        if(document.getElementById("standard_test_target").value==="other")
        {
            standard_test_ip = regexIP.test(document.getElementById("standard_test_ip").value);
        }
    }

    if(document.getElementById("speedtest").checked===true && document.getElementById("speedtest_target").value==="other")
    {
        speedtest_ip = regexIP.test(document.getElementById("speedtest_ip").value);
        speedtest_port = document.getElementById("speedtest_port").value >= input["int"]["speedtest_port"]["Min"] && document.getElementById("speedtest_port").value <= input["int"]["speedtest_port"]["Max"];
    }

    if(document.getElementById("autotest") && document.getElementById("autotest").checked===true)
    {
        autotest = document.getElementById("autotest_target").value >= input["int"]["autotest_target"]["Min"] && document.getElementById("autotest_target").value <= input["int"]["packet_number"]["Max"];
    }

    if(oneRadioChecked && packetNumber && packetTimeout && standard_test_ip && speedtest_ip && speedtest_port && probeFree && autotest && comments)
    {
        document.getElementById("start_test").removeAttribute("disabled");
    }
    else
    {
        document.getElementById("start_test").setAttribute("disabled", "disabled");
    }
}

