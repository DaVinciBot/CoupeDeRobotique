// if img src point to smth, then it will be displayed
let cam = document.querySelector('.cam');
let no_signal = document.querySelector('.make_center h1');

let img = document.createElement('img');
img.src = 'http://127.0.0.1:8001/cam.mjpg';
img.style.visibility = 'hidden';
img.style.display = 'none';

document.body.appendChild(img);


// check if the image is loaded
img.onload = function() {
    console.log('loaded');
    switch_source(img.src);

};

function switch_source(src = "") {
    if (src == ""){
        cam.style.backgroundImage = 'url("../assets/no_signal.png")';
        no_signal.style.display = 'block';
    } else {
        cam.style.backgroundImage = 'url(' + src + ')';
        no_signal.style.display = 'none';
    }
}