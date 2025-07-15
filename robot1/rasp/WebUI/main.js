// let console_div = document.getElementById('log');

let log = new WebSocketManager();
log.add_ws("ui")
log.add_handler("ui", (event) => {
    // Parse the JSON message and display the console data
    let data = JSON.parse(event.data);
    if (data.msg === "update ui data") {
        // show_console_data(JSON.stringify(data.data), true);

        const jack_state = document.getElementById("jack_state");
        jack_state.style.backgroundColor = data.data["jack_state"] ? "limegreen" : "red";
        if (data.data["jack_state"]) {
            jack_state.innerText = "Ready"
        } else if(jack_state.innerText == "Ready") {
            jack_state.innerText = "Not Ready";
            startTimer();
        }

        const bau_state = document.getElementById("bau_state");
        bau_state.style.backgroundColor = data.data["BAU"] ? "limegreen" : "red";
        bau_state.innerText = data.data["BAU"] ? "ON" : "ACTIVATED";

        const score = document.getElementById("score");
        //score.innerText = data.data["score"] ? data.data["score"] : "000";

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

let buttons = document.querySelectorAll(".button");
buttons.forEach(button => {
    button.addEventListener("click", () => {
        button_click_effect(button, log);
    })
});

function startTimer() {
    const timer = document.getElementById("timer");
    let countdown = new Date().getTime() + 1000 * 60 + 1000 * 40;
    let x = setInterval(function() {
        let now = new Date().getTime();
        let distance = countdown - now;

        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        timer.innerHTML = minutes + ":" + seconds;

        if (distance < 0) {
            clearInterval(x);
            timer.innerHTML = "FINISHED";
        }
        else if (distance < 1000 * 15) {
            timer.style.backgroundColor = "orange";
        }
    }, 1000);
}

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