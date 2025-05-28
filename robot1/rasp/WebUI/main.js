// let console_div = document.getElementById('log');

let log = new WebSocketManager();
log.add_ws("ui")
log.add_handler("ui", (event) => {
    // Parse the JSON message and display the console data
    let data = JSON.parse(event.data);
    if (data.msg === "update ui data") {
        // show_console_data(JSON.stringify(data.data), true);

        let jack_state = document.getElementById("jack_state");
        jack_state.style.backgroundColor = data.data["Tirette"] ? "limegreen" : "red";
        jack_state.innerText = data.data["Tirette"] ? "Ready" : "Not Ready";

        let bau_state = document.getElementById("bau_state");
        bau_state.style.backgroundColor = data.data["BAU"] ? "limegreen" : "red";
        bau_state.innerText = data.data["BAU"] ? "ON" : "ACTIVATED";

        for (let pami in data.data["pamis_states"]) {
            let element = document.getElementById(`${pami}_state`);
            element.style.backgroundColor = data.data["pamis_states"][pami] ? "limegreen" : "red";
        }
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