// let console_div = document.getElementById('log');

let log = new WebSocketManager();
log.add_ws("ui")
log.add_handler("ui", (event) => {
    // Parse the JSON message and display the console data
    let data = JSON.parse(event.data);
    if (data.msg === "update ui data") {
        // show_console_data(JSON.stringify(data.data), true);

        const jack_state = document.getElementById("jack_state");
        jack_state.style.backgroundColor = data.data["Tirette"] ? "limegreen" : "red";
        jack_state.innerText = data.data["Tirette"] ? "Ready" : "Not Ready";

        const bau_state = document.getElementById("bau_state");
        bau_state.style.backgroundColor = data.data["BAU"] ? "limegreen" : "red";
        bau_state.innerText = data.data["BAU"] ? "ON" : "ACTIVATED";

        const pamis_states = document.getElementById('pami_states');
        pamis_states.innerHTML = '';
        for (let pami in data.data["pamis_states"]) {
            const card = document.createElement('div');
            card.dataset.id = `${pami}_state`;
            card.style.backgroundColor = data.data["pamis_states"][pami] ? "limegreen" : "red";
            card.style.padding = "10px";
            card.style.borderRadius = "20px";
            card.style.color = "white";
            card.style.fontWeight = "bold";
            card.innerHTML = pami;
            pamis_states.append(card);
        };
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