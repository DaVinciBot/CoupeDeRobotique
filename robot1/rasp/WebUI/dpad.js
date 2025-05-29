let ws = new WebSocketManager();
ws.add_ws("cmd");

let actionneurs_state = false

let up = document.querySelector(".up");
let down = document.querySelector(".down");
let left = document.querySelector(".left");
let right = document.querySelector(".right");

let actionneurs = document.querySelector(".actionneurs")
let clear = document.querySelector(".clear")
let reset = document.querySelector(".reset")

up.addEventListener("click", function (event) {
    send_dir("self.rolling_basis.go_to_relative(Point(50,0))")
});

down.addEventListener("click", function (event) {
    send_dir("self.rolling_basis.go_to_relative(Point(-50,0))")
});

left.addEventListener("click", function (event) {
    send_dir("self.rolling_basis.go_to_relative(Point(1,-1))")
});

down.addEventListener("click", function (event) {
    send_dir("self.rolling_basis.go_to_relative(Point(1,1))")
});

clear.addEventListener("click", function (event) {
    send_dir("self.rolling_basis.stop_and_clear_queue()")
})
reset.addEventListener('click', function (event) {
    send_dir("self.rolling_basis.reset_odo()")
})

actionneurs.addEventListener("click", function (event){
    if (actionneurs_state){
        send_dir("self.open_god_hand()")
        actionneurs_state = false
    } else {
        send_dir("self.close_god_hand()")
        actionneurs_state = true
    }
})


function send_dir(msg) {
    //ws.send("cmd", "eval", "self.rolling_basis.reset_odo()");
    ws.send("cmd", "eval", msg);
}