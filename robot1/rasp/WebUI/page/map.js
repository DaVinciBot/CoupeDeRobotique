let wsm = new WebSocketManager();
wsm.add_ws("odometer");
wsm.add_handler("odometer", (event) => {
    console.log(event.data);
    let data = JSON.parse(event.data)["data"];
    y = data[0];
    x = data[1];
    theta = data[2];
    parse_pos();
    set_rob_pos();
});

let rob = document.querySelector(".rob");

let x = 0, y = 0, theta = 0;

function parse_pos() {
    x = Math.min(parseFloat(x) * 4.896, 1469); // Max width in pixels, adjusted to actual width
    y = Math.min(parseFloat(y) * 4.9, 980); // Max height in pixels, adjusted to actual height
    theta = parseFloat(theta) * 180 / Math.PI + 90; // Convert radians to degrees
}

function set_rob_pos() {
    if (rob) {
        rob.style.transformOrigin = "top left";
        rob.style.transform = `translate(${x}px, ${y}px) rotate(${theta}deg)`;
    } else {
        console.error('Robot element not found.');
    }
}