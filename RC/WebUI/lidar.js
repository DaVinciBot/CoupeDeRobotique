let canvas = document.getElementById("lidar");
let ctx = canvas.getContext("2d");
ctx.translate(0.5, 0.5);

let max_range = document.getElementById("max_range");
let MAX_DISTANCE = max_range.valueAsNumber; // meters
max_range.addEventListener("input", function () {
    MAX_DISTANCE = max_range.valueAsNumber;
    draw();
});

let width = canvas.width;
let height = canvas.height;

let centerX = width / 2;
let centerY = height / 2;

let radius = 100;
let angle = 0;



let lidarData = [];
for (let i = 0; i < 270 * 3; i++) {
    lidarData.push(5);
}

let lidar = new WebSocket("ws://127.0.0.1:3000/lidar");
lidar.onmessage = function (event) {
    if (event.data.startsWith("new$=$") || event.data.startsWith("current$=$")) {
        let data = event.data.split("$=$")[1].split(",");
        for (let i = 0; i < data.length; i++) {
            lidarData[i] = parseFloat(data[i]);
        }
        draw();
    }
}

function toggle_alt_design() {
    alt_design = !alt_design;
    draw();
}

function draw_red_dot(){
    // center dot
    ctx.fillStyle = "red";
    ctx.fillRect(centerX - 2.5, centerY - 2.5, 5, 5);
}

function overlay() {
    // full circle
    ctx.beginPath();
    ctx.strokeStyle = "red";
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fillStyle = "#095af1";
    ctx.fill()
    ctx.stroke();
    ctx.fillStyle = "red";
    ctx.fillRect(centerX - 2.5, centerY - 2.5, 5, 5);
    // diameter line
    ctx.beginPath();
    ctx.strokeStyle = "red";
    ctx.moveTo(centerX - radius - 5, centerY - radius);
    ctx.lineTo(centerX - radius - 15, centerY - radius);
    ctx.moveTo(centerX - radius - 10, centerY - radius);
    ctx.lineTo(centerX - radius - 10, centerY + radius);
    ctx.moveTo(centerX - radius - 15, centerY + radius);
    ctx.lineTo(centerX - radius - 5, centerY + radius);
    ctx.stroke();
    // diameter size text
    ctx.fillStyle = "red";
    ctx.font = "15px Arial";
    ctx.fillText(`${MAX_DISTANCE * 2}m`, centerX - radius - 60, centerY);
}

function draw_data(decalage = 45) {
    ctx.strokeStyle = "#fff";
    for (let i = 0; i < lidarData.length; i++) {
        let angle = i * (1 / 3) * -Math.PI / 180 + decalage * Math.PI / 180;
        let distance = lidarData[i] > MAX_DISTANCE || lidarData[i] < 0.001 ? radius : lidarData[i] * (radius / MAX_DISTANCE);
        draw_line(angle, distance);
    }
}

function draw_line(angle, distance) {
    let x = centerX + distance * Math.cos(angle);
    let y = centerY + distance * Math.sin(angle);
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(x, y);
    ctx.stroke();
}

function draw() {
    ctx.clearRect(0, 0, width, height);
    overlay()
    draw_data();
    draw_red_dot();
}

document.addEventListener("DOMContentLoaded", function () {
    lidar.onopen = function () {
        console.log("lidar connected");
        lidar.send("get");
    }
    draw();
});
