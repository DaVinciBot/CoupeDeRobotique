let ws = new WebSocketManager();
ws.add_ws("cmd");

let maki = document.querySelectorAll(".maki");
let plus = document.querySelector("#plus");
let minus = document.querySelector("#minus");
let input = document.querySelector("#input");
let range = document.querySelector("#power");

let current_maki = null;


for (let i = 0; i < maki.length; i++) {
    maki[i].addEventListener("click", () => {
        focus_maki(maki[i]);
    })
}

function focus_maki(c_maki) {
    for (let i = 0; i < maki.length; i++) {
        maki[i].classList.remove("active");
    }
    c_maki.classList.add("active");
    current_maki = c_maki;
    input.value = c_maki.children[0].innerText;
}

plus.addEventListener("click", () => {
    if (current_maki != null) {
        let value = parseFloat(input.value);
        value += parseFloat(range.value);
        value = Math.round(value * 100) / 100;
        input.value = value;
        current_maki.children[0].innerText = value;
    }
})

minus.addEventListener("click", () => {
    if (current_maki != null) {
        let value = parseFloat(input.value);
        value -= parseFloat(range.value)
        value = Math.round(value * 100) / 100;
        input.value = value;
        current_maki.children[0].innerText = value;
    }
})




let kp = document.querySelector("#kp");
let ki = document.querySelector("#ki");
let kd = document.querySelector("#kd");

let start_speed = document.querySelector("#start_speed");
let start_distance = document.querySelector("#start_distance");
let end_speed = document.querySelector("#end_speed");
let end_distance = document.querySelector("#end_distance");

let max_speed = document.querySelector("#max_speed");
let timeout = document.querySelector("#timeout");
let allowed_error = document.querySelector("#allowed_error");
let precision = document.querySelector("#precision");
let correction_speed = document.querySelector("#correction_speed");

let x = document.querySelector("#x");
let y = document.querySelector("#y");
let theta = document.querySelector("#theta");

let send = document.querySelector("#send");

send.addEventListener("click", () => {
    ws.send("cmd", "eval", `self.rolling_basis.set_pid(${kp.value}, ${ki.value}, ${kd.value})`);
    ws.send("cmd", "eval", `self.rolling_basis.go_to(Point(${x.value}, ${y.value}), forward=True, max_speed=${max_speed.value}, next_position_delay=${timeout.value}, action_error_auth=${allowed_error.value}, traj_precision=${precision.value}, correction_trajectory_speed=${correction_speed.value}, acceleration_start_speed=${start_speed.value}, acceleration_distance=${start_distance.value}, deceleration_end_speed=${end_speed.value}, deceleration_distance=${end_distance.value})`);
})
