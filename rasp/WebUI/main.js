let console_div = document.querySelector('.console')
let state_div = document.querySelector('.state')

let log = new WebSocket("ws://localhost:3000/log");
log.onmessage = function (event) {
    if (event.data.startsWith("current$=$")) {
        show_console_data(event.data.split("$=$")[1].replaceAll('"', '').replace('[', '').replace(']', '').split(",").join('<br>'))
    }
    if (event.data.startsWith("new$=$")){
        show_console_data(event.data.split("$=$")[1].replace('["', '').replace('"]', '')+"<br>", true)
    }
}

function show_console_data(data, add=false) {
    if (add) {
        console_div.innerHTML += data
    } else {
        console_div.innerHTML = data
    }
    // scroll to bottom if the user is not scrolling up
    if (console_div.scrollTop >= (console_div.scrollHeight - console_div.offsetHeight - 1000)) {
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