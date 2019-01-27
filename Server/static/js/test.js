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

const regexComment = new RegExp("^[a-zA-Z0-9@-_'\".()àéè&=+~^*!:?,<>ç{}%¨ ]*$");
let timer = 6;
let refreshIntervalId;

document.addEventListener('DOMContentLoaded', () => {
    refreshIntervalId = setInterval(refresh, 1000);
});

function get_test_info()
{
    if(document.getElementById("status").value === "waiting")
    {
        fetch('/api?test_info=1&id=' + document.getElementById("test_id_origin").value).then(function(response) {
        return (response.text());
        })
        .then(function(responseText)
        {
            if(document.getElementById("test_info").innerHTML !== responseText)
            {
                document.getElementById("test_info").innerHTML = responseText;
            }
        })
        .catch(function(error)
        {
            console.log('Fetch API error: ' + error.message);
            document.getElementById("test_info").innerHTML = "<article class=\"message is-danger\"><div class=\"message-header\"><p>Error !</p></div><div class=\"message-body\"><span class=\"has-text-danger\"><span class=\"icon\"><i class=\"fas fa-ban\" aria-hidden=\"true\"></i></span>" + "Fetch API Error: " + error.message + "</span></div></article><br><div class=\"container has-text-centered\"><a class=\"button is-info\" href=\"/archive\"><span class=\"icon is-small\"><i class=\"fas fa-chevron-circle-right\"></i></span><span>Go back to archive</span></a></div>";
        });
    }
}

function refresh()
{
    if(document.getElementById("refresh_timer") != null)
    {
        if(timer > 0)
        {
           timer = timer - 1;
        }

        if (timer >= 1) {
            document.getElementById("refresh_timer").innerHTML = "Refresh in " + timer + "s";
        }
        else
        {
            document.getElementById("refresh_timer").innerHTML = "Refreshing now ...";
            timer = 6;
            get_test_info();
        }
        return timer;
    }
    else
    {
        if(document.getElementById("comments") != null)
        {
            document.getElementById("comments").addEventListener("keyup", function () {
                disableFormTest("comments", 0, 500, regexComment);
            }, {passive: true});
            document.getElementById("comments").dispatchEvent(new Event("keyup"));
        }
        if(document.getElementById("display_download_json") != null)
        {
            display_json("display_download_json", "download_json");
        }
        if(document.getElementById("display_upload_json") != null)
        {
            display_json("display_upload_json", "upload_json");
        }
        if(document.getElementById("copy_download_json") != null)
        {
            copy_json("copy_download_json", "download_json");
        }
        if(document.getElementById("copy_upload_json") != null)
        {
            copy_json("copy_upload_json", "upload_json");
        }
        clearInterval(refreshIntervalId);
    }
}

function display_json(display_id, field)
{
    document.getElementById(display_id).addEventListener("click", function () {
        if(document.getElementById(display_id).classList.contains("is-info"))
        {
            document.getElementById(display_id).classList.remove("is-info");
            document.getElementById(display_id).classList.add("is-danger");

            document.getElementById(display_id).innerHTML = "<span class=\"icon is-small\"><i class=\"fas fa-eye-slash\"></i></span><span>Hide JSON</span>";

            document.getElementById(field).classList.remove("is-hidden");
        }
        else
        {
            document.getElementById(display_id).classList.remove("is-danger");
            document.getElementById(display_id).classList.add("is-info");

            document.getElementById(display_id).innerHTML = "<span class=\"icon is-small\"><i class=\"fas fa-eye\"></i></span><span>Display JSON</span>";

            document.getElementById(field).classList.add("is-hidden");
        }
    }, {passive: true});
}

function copy_json(copy_id, field)
{
    document.getElementById(copy_id).addEventListener("click", function () {
        let copyText = document.getElementById(field).children[0].innerHTML;
        let textArea = document.createElement('textarea');
        textArea.value = copyText;
        document.getElementById(copy_id).appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        textArea.remove();
        document.getElementById(copy_id).classList.add("is-loading");
        document.getElementById(copy_id).classList.remove("is-info");
        document.getElementById(copy_id).classList.add("is-warning");
        setTimeout(function(){document.getElementById(copy_id).classList.remove("is-loading"); document.getElementById(copy_id).classList.remove("is-warning"); document.getElementById(copy_id).classList.add("is-info");}, 500);
    }, {passive: true});
}

function disableFormTest(id, min_length, max_length, regex)
{
    let inputObject = document.getElementById(id);

    if(inputObject.value.length >= min_length && inputObject.value.length <= max_length && regex.test(inputObject.value))
    {
        document.getElementById("save_test").removeAttribute("disabled");

        inputObject.classList.add("is-success");
        inputObject.classList.remove("is-danger");
    }
    else
    {
        document.getElementById("save_test").setAttribute("disabled", "disabled");

        inputObject.classList.add("is-danger");
        inputObject.classList.remove("is-success");
    }
}