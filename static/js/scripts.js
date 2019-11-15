/**
 * Created by Otoniel on 20/11/2016.
 */
function updateViewLibroDiario() {
    var num = document.getElementById("fnum").value;
    var str = getToken(0);

    if (num == 0) {
        document.getElementById("form-container").innerHTML = "";
        return null;
    }

    requestPost("/get_movimiento_form/", "mov="+num+"&csrfmiddlewaretoken="+str);
}

function getToken(index) {
    return document.getElementsByName("csrfmiddlewaretoken")[index].value;
}

//Se necesita de un objeto conetendor llamado: "form-container"
function requestGet(destino) {
    handler = new XMLHttpRequest();

    handler.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            container = document.getElementById("form-container");
            container.innerHTML = "";
            container.innerHTML = this.responseText;
        }
        if(this.status == 403 || this.status == 404) {
            document.getElementById("form-container").innerHTML = "Atención: " + this.status;
        }
    };

    handler.open("GET", destino, true);
    handler.send();
}

//Se necesita de un objeto conetendor llamado: "form-container"
function requestGetParameters(destino, parameters) {
    handler = new XMLHttpRequest();

    handler.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            container = document.getElementById("form-container");
            container.innerHTML = "";
            container.innerHTML = this.responseText;
        }
        if(this.status == 403 || this.status == 404) {
            document.getElementById("form-container").innerHTML = "Atención: " + this.status;
        }
    };

    handler.open("GET", destino+"?"+parameters, true);
    handler.send();
}

//Se necesita de un objeto conetendor llamado: "form-container"
function requestPost(destino, parameters) {
    handler = new XMLHttpRequest();

    handler.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            container = document.getElementById("form-container");
            container.innerHTML = "";
            container.innerHTML = this.responseText;
        }
        if(this.status == 403 || this.status == 404) {
            document.getElementById("form-container").innerHTML = "Atención: " + this.status;
        }
    };

    handler.open("POST", destino, true);
    handler.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    handler.send(parameters);
}
