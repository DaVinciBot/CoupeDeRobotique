let console_div = document.querySelector('.log')

let log = new WebSocket(`ws://${host}:${port}/log?sender=${user}`);
log.onmessage = function (event) {
    // parse JSON then display it
    let data = JSON.parse(event.data);
    if (data.msg == "Msg received") {
        show_console_data(data.data, true)
    }
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

log.onopen = function () {
    console.log("log connected");
}
