const file_config = document.getElementById('file_config');
const file_update = document.getElementById('file_update');

const form_delete = document.getElementById('form_delete');
const form_config = document.getElementById('form_config');
const form_update = document.getElementById('form_update');

form_delete.addEventListener('submit', async (e) => {
    e.preventDefault();
    function fetchData() {
        var apiUrl = 'http://localhost:5000/api/v1/';
        fetch(apiUrl, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/xml',
            }
        })
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    throw new Error('Error en la solicitud DELETE');
                }
            })
            .then(data => {
                const xml = formatXML(data);
                openModal(xml);
            })
            .catch(error => {
                const xml = formatXML(error);
                openModal(xml);
            })
    }
    fetchData();
});

form_config.addEventListener('submit', async (e) => {
    e.preventDefault();
    async function fetchData() {
        const file = file_config.files[0];
        const data = await leerArchivo(file);
        var apiUrl = 'http://localhost:5000/api/v1/';
        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/xml',
            },
            body: data
        })
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    throw new Error('Error en la solicitud POST');
                }
            })
            .then(data => {
                const xml = formatXML(data);
                openModal(xml);
            })
            .catch(error => {
                const xml = formatXML(error);
                openModal(xml);
            })
    }
    await fetchData();
});

form_update.addEventListener('submit', async (e) => {
    e.preventDefault();
    async function fetchData() {
        const file = file_update.files[0];
        const data = await leerArchivo(file);
        var apiUrl = 'http://localhost:5000/api/v1/';
        fetch(apiUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/xml',
            },
            body: data
        })
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    throw new Error('Error en la solicitud PUT');
                }
            })
            .then(data => {
                const xml = formatXML(data);
                openModal(xml);
            })
            .catch(error => {
                const xml = formatXML(error);
                openModal(xml);
            })
    }
    await fetchData();
});


function leerArchivo(archivo) {
    return new Promise((resolve, reject) => {
        if (!archivo) {
            reject('Archivo no encontrado');
        }
        var lector = new FileReader();
        lector.onload = function (e) {
            var contenido = e.target.result;
            resolve(contenido);
        };
        lector.onerror = function (e) {
            reject('Error al leer el archivo');
        };
        lector.readAsText(archivo);
    });
}


// Función para abrir el modal
function openModal(rexml) {
    document.getElementById("myModal").style.display = "block";
    // agregar saltos de línea al XML
    rexml = rexml.replace(/></g, ">\n<");
    document.getElementById("respuesta").innerHTML = rexml;

}

// Función para cerrar el modal
function closeModal() {
    document.getElementById("myModal").style.display = "none";
    window.location.reload();
}

function formatXML(xmlString) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlString, "text/xml");
    const formattedXML = new XMLSerializer().serializeToString(xmlDoc.documentElement);
    return formattedXML;
  }