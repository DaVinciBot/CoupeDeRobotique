let canvas = document.getElementById("lidar");
let ctx = canvas.getContext("2d");
ctx.translate(0.5, 0.5);


let width = canvas.width;
let height = canvas.height;

let centerX = width / 2;
let centerY = height / 2;

let radius = 100;
let angle = 0;

let lidarData = [];
for (let i = 0; i < 270*3; i++) {
    lidarData.push(5);
}

let lidar = new WebSocket("ws://127.0.0.1:3000/lidar");
lidar.onmessage = function (event) {
    console.log(event.data);
    if (event.data.startsWith("new:") || event.data.startsWith("current:")) {
        let data = event.data.split(":")[1].split(",");
        for (let i = 0; i < data.length; i++) {
            lidarData[i] = parseFloat(data[i]);
        }
        draw();
    }
}

function overlay() {
    ctx.fillStyle = "red";
    ctx.fillRect(centerX - 2.5, centerY - 2.5, 5, 5);
    ctx.beginPath();
    ctx.strokeStyle = "red";
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.stroke();
}

function draw_data(decalage = 45) {
    ctx.strokeStyle = "#095af1";
    for (let i = 0; i < lidarData.length; i++) {
        let angle = i * (1 / 3) * -Math.PI / 180 + decalage * Math.PI / 180;
        let distance = lidarData[i]*(radius/10);
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
    draw_data();
    overlay();
    
}

document.addEventListener("DOMContentLoaded", function () {
    lidar.onopen = function () {
        console.log("lidar connected");
        // send "get" and parse the response
        lidar.send("get");
    }
    draw();
});
