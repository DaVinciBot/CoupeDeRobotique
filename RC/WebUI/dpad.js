let up = document.querySelector(".up");
let down = document.querySelector(".down");
let left = document.querySelector(".left");
let right = document.querySelector(".right");

let refresh = document.querySelector("#refresh");

let robot = new WebSocket("ws://127.0.0.1:3000/cmd");
robot.onopen = function () {
    console.log("/cmd connected");
}

let dpad_divs = [...up.children,...down.children,...left.children,...right.children];
for (let i = 0; i < dpad_divs.length; i++) {
    dpad_divs[i].addEventListener("click", function (event) {
        let direction = event.target.parentElement.className;
        let msg = "";
        if (direction == "up") {
            msg = "[10,0,0]";
        } else if (direction = "down") {
            msg = "[-10,0,0]";
        } else if (direction = "left") {
            msg = "[0,10,0]";
        } else if (direction = "right") {
            msg = "[0,-10,0]";
        }
        robot.send("set$=$goto"+msg);
    });
}

refresh.addEventListener("click", function (event) {
    robot.send("set$=$home");
});
