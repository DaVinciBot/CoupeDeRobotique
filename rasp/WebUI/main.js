let console_div = document.querySelector('.console')
let state_div = document.querySelector('.state')

let log = new WebSocket("ws://127.0.0.1:3000/log");
log.onmessage = function (event) {
    console.log(event.data);
    if (event.data.startsWith("new:") || event.data.startsWith("current:")) {
        show_console_data(event.data.split(",").join('\n'))
    }
}

function show_console_data(data) {
    console_div.innerText = data
    // scroll to bottom if the user is not scrolling up
    if (console_div.scrollTop >= (console_div.scrollHeight - console_div.offsetHeight - 1000)) {
        console.log(console_div.scrollTop - (console_div.scrollHeight - console_div.offsetHeight - 100))
        console_div.scrollTop = console_div.scrollHeight
    }

}
console.scrollTop = console.scrollHeight

document.addEventListener("DOMContentLoaded", function () {
    log.onopen = function () {
        console.log("log connected");
        // send "get" and parse the response
        log.send("get");
    }
})