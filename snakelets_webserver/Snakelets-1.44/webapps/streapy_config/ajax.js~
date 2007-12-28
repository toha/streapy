// XMLHTTP - Request machen und nach dem fertig stellen, eine uebergebene handler_function aufrufen

    var http_request = false;

    function macheRequest(url, handler_function) {
        //alert(url);
        http_request = false;

        if (window.XMLHttpRequest) { // Mozilla, Safari,...
            http_request = new XMLHttpRequest();
            if (http_request.overrideMimeType) {
                http_request.overrideMimeType('text/xml');
                // zu dieser Zeile siehe weiter unten
            }
        } else if (window.ActiveXObject) { // IE
            try {
                http_request = new ActiveXObject("Msxml2.XMLHTTP");
            } catch (e) {
                try {
                    http_request = new ActiveXObject("Microsoft.XMLHTTP");
                } catch (e) {}
            }
        }

        if (!http_request) {
            return false;
        }
        http_request.onreadystatechange = handler_function;
        http_request.open('GET', url, true);
        http_request.send(null);

    }
    
    
