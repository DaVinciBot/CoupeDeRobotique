let console_div = document.querySelector('.log')

let log = new WebSocketManager();
log.add_ws("ui")
log.add_handler((event) => {
    // Parse the JSON message and display the console data
    let data = JSON.parse(event.data);
    if (data.msg === "update ui data") {
        show_console_data(JSON.stringify(data.data), true);

        let jack_state = document.getElementById("Tirette");
        let bau_state = document.getElementById("BAU");

        jack_state.style.backgroundColor = data.data["Tirette"] ? "limegreen" : "red";
        bau_state.style.backgroundColor = data.data["BAU"] ? "limegreen" : "red";

        //TODO:PAMI
        // for (let key in data.data) {
        //     if (data.data.hasOwnProperty(key)) {
        //         let element = document.getElementById(key);
        //         if (element) {
        //             // Si la valeur est un objet imbriqué, on l'affiche sous forme de chaîne JSON
        //             if (typeof data.data[key] === 'object') {
        //                 element.innerText = JSON.stringify(data.data[key]);
        //             } else {
        //                 element.innerText = data.data[key];
        //             }
        //         }
        //     }
        // }
    }
});

function show_console_data(data, add = false) {
    if (add) {
        console_div.innerHTML += data + "<br>"
    } else {
        console_div.innerHTML = data
    }
    // scroll to bottom if the user is not scrolling up
    if (console_div.scrollTop >= (console_div.scrollHeight - console_div.offsetHeight - 1000)) {
        console_div.scrollTop = console_div.scrollHeight
    }

}
console.scrollTop = console.scrollHeight