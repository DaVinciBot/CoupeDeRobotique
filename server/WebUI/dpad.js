let cmd_ws = new WebSocket(`ws://${host}:${port}/cmd?sender=${user}`);

let up = document.querySelector(".up");
let down = document.querySelector(".down");
let left = document.querySelector(".left");
let right = document.querySelector(".right");

let dpad_divs = [...up.children, ...down.children, ...left.children, ...right.children];
for (let i = 0; i < dpad_divs.length; i++) {
    dpad_divs[i].addEventListener("click", function (event) {
        let direction = event.target.parentElement.className;
        let msg = direction + "$=$" + 100;
        console.log(msg);
    });
    dpad_divs[i].addEventListener("mousedown", function (event) {
        let direction = event.target.parentElement.className;
        let msg = direction + "$=$";
        console.log(msg);
    });
    dpad_divs[i].addEventListener("mouseup", function (event) {
        let direction = event.target.parentElement.className;
        let msg = direction + "$=$" + 0;
        console.log(msg);
    });
}

cmd_ws.onopen = function () {
    console.log("dpad connected");
}