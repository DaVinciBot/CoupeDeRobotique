class WebSocketManager {
    constructor() {
        this.websockets = {};
        this.host = "rc.local";
        this.port = "8080";
        this.user = "WebUI";
    }

    #create_trame(msg, data) { 
        let ts = Date.now();
        let usr = this.user;
        return JSON.stringify({ usr, msg, data, ts })
    }
    
    #ws_connect(route) {
        return new WebSocket(`ws://${this.host}:${this.port}/${route}?sender=${this.user}`)
    }

    add_ws(route) {
        this.websockets[route] = this.#ws_connect(route)
        this.websockets[route].onopen = function () {
            console.log(`${route} connected`);
        }
        // hold until the connection is established and timeout < 1s
        // let start = Date.now()
        // while (this.websockets[route].readyState !== 1 && Date.now - start < 2000) {}
        return this.websockets[route]
    }

    add_handler(route, handler) {
        this.websockets[route].onmessage = handler
    }

    send(route, msg, data) {
        this.websockets[route].send(this.#create_trame(msg, data))
    }
}

// change background color of button during .05s when clicked
function button_click_effect(button) {
    button.style.backgroundColor = "#0232FF";
    setTimeout(() => {
        button.style.backgroundColor = "#B3C2FF";
    }, 50)
}

let buttons = document.querySelectorAll(".button");
buttons.forEach(button => {
    button.addEventListener("click", () => {
        button_click_effect(button);
    })
})