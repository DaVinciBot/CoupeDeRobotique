let position_ws = new WebSocket(`ws://${host}:${port}/odometer?sender=${user}`);
let rob = document.querySelector(".rob")

let x = 0
let y = 0
let theta = 0

// Dimension en pixel : 1489 x 1000 px
// Dimension en mètre : 3 x 2 m
// en X : 1 m = 496.33 px | 1cm = 4.96 px
// en Y : 1 m = 500 px    | 1cm = 5 px

position_ws.onmessage = function (event) {
    data = JSON.parse(event.data);
    [x, y, theta] = 0, 0, 0
    parse_pos()
    set_rob_pos()
}

function parse_pos() {
    x = Math.min(parseFloat(x) * 4.9633, 300 * 4.9633)
    y = Math.min(parseFloat(y) * 5.0, 200 * 5)
    theta = parseFloat(theta) * 180 / Math.PI
}

function set_rob_pos() {
    rob.style.transformOrigin = "top left"
    rob.style.transform = `translate(${x}px, ${y}px) rotate(${theta}deg)`
}

position_ws.onopen = function () {
    console.log("map connected");
}
